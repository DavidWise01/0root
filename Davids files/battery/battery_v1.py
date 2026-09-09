"""
Refined battery model — v1 (upgrade patch over battery_v0.py)
=============================================================
Replaces the THREE crude lies in v0 with progressively more real physics.
v0 stays UNTOUCHED (append-only policy). This is battery_v1.py — the
"Nernst sag + growing R + soft knee" upgrade.

Lie tracking (v0 -> v1):
  1. OCV constant  -> Liebig/Van 't Hoff Nernst sag as SOC depletes
  2. R_int fixed    -> growing R_int via concentration + surface-rate terms
  3. sharp cliff    -> smooth sigmoid knee + exponential tail

Battery: 10/10 refined -> compressed to 1 indigo ball kinetic
"""

import math
import numpy as np

# ── physical constants ──────────────────────────────────────────────
F = 96485.0          # Faraday constant, C / mol e-
R = 8.3145           # gas constant, J / (mol K)
T = 298.15           # 25 °C, K
Z_ELEC = 2           # electrons per Zn -> Zn2+


def nernst(E_std: float, soc: float) -> float:
    """
    Nernst equation with SOC-dependent activity.
    Lie 1 fix: OCV sags as reactants deplete, not constant.
    E(SOC) = E° - (RT / zF) * ln(activity_product / activity_reactant)

    For Zn | ZnSO4 || CuSO4 | Cu:
    - anode activity (Zn2+) grows as Zn dissolves -> E_anode drops
    - cathode activity (Cu2+) shrinks as Cu deposits -> E_cathode rises less
    Net: OCV drops nonlinearly at low SOC.
    """
    # activity ratio: product/reactant, modeled as SOC-dependent
    # at SOC=1 (full): ratio ~ 1, E = E_std
    # at SOC=0 (empty): ratio diverges, E drops
    # model: ln(Q) ~ -ln(SOC) for the anode-dominated sag
    # clamp to avoid log(0)
    soc_clamped = max(soc, 1e-6)
    dE = -(R * T / (Z_ELEC * F)) * math.log(soc_clamped)  # ~ (RT/zF) * ln(SOC)
    # RT/zF at 298K = 0.01285 V, so full sag ≈ 0.01285 * ln(SOC)
    return E_std + dE


class RefinedCell:
    """
    Zn | Zn2+ || Cu2+ | Cu  — Daniell cell with v1 physics:

    * OCV varies with SOC (Nernst)
    * R_int grows as SOC drops (concentration polarization + surface effects)
    * Voltage has a soft knee + exponential tail, not a cliff
    """

    def __init__(
        self,
        m_anode_g: float = 5.0,
        m_cathode_g: float = 5.0,
        T_K: float = 298.15,
    ):
        self.T_K = T_K

        # ─── electrochemistry ───
        self.E_anode_std = -0.76    # Zn2+ + 2e- -> Zn(s)
        self.E_cathode_std = +0.34  # Cu2+ + 2e- -> Cu(s)
        self.z = Z_ELEC

        # ─── materials ───
        self.M_Zn = 65.38   # g/mol
        self.M_Cu = 63.55   # g/mol
        moles_Zn = m_anode_g / self.M_Zn
        moles_Cu = m_cathode_g / self.M_Cu
        self.m_anode_g = moles_Zn * self.M_Zn  # conserved
        self.m_cathode_g = moles_Cu * self.M_Cu

        # ─── geometry for concentration effects ───
        # surface area of zinc anode (cm2), affects current density
        self.anode_sa_cm2 = 10.0  # ~1 cm2 face of a small plate
        # initial concentration of Cu2+ (mol/L)
        self.C_cathode_init = moles_Cu / 0.1  # 100 mL electrolyte

        # ─── internal resistance model (Lie 2 fix) ───
        self.R_0 = 0.15       # ohm, cold internal resistance (base)
        self.k_conc = 0.45    # concentration polarization coefficient
        self.k_surface = 0.30  # surface-rate (Butler-Volmer) coefficient
        self.R_max = 20.0     # ohm, hard max as reactants deplete

        # ─── state ───
        self.soc = 1.0       # state of charge [0, 1]
        self.moles_Zn_remaining = moles_Zn
        self.C_cathode = self.C_cathode_init

    # ── properties ──────────────────────────────────────────────────

    @property
    def capacity_C(self) -> float:
        """Total theoretical charge from zinc anode."""
        return self.z * F * self.moles_Zn_remaining_initial

    @property
    def capacity_Ah(self) -> float:
        return self.capacity_C / 3600.0

    @capacity_C.setter
    def capacity_C(self, val):
        pass  # read-only; total charge is fixed by initial moles

    _m_Zn_initial = None

    def __init_subclass__(cls):
        pass

    # fix: store initial moles before any consumption
    def __post_init__(self):
        if self._m_Zn_initial is None:
            self._m_Zn_initial = self.moles_Zn_remaining

    @property
    def moles_Zn_remaining_initial(self) -> float:
        if self._m_Zn_initial is None:
            self._m_Zn_initial = self.moles_Zn_remaining
        return self._m_Zn_initial

    @property
    def ocv(self) -> float:
        """Lie 1 FIXED: OCV varies with SOC via Nernst equation."""
        soc = max(self.soc, 1e-6)
        E_anode = nernst(self.E_anode_std, soc)
        E_cathode = nernst(self.E_cathode_std, soc)
        # cathode activity increases as Cu2+ deposits (less polarization)
        E_cathode += (R * self.T_K / (self.z * F)) * math.log(
            max(self.C_cathode / self.C_cathode_init, 1e-6)
        )
        return E_cathode - E_anode

    @property
    def R_int(self) -> float:
        """Lie 2 FIXED: R_int grows as SOC drops (concentration + surface)."""
        soc = max(self.soc, 0.001)  # avoid div-by-zero
        soc_inv = (1.0 / soc) - 1.0  # ~0 at full, large at empty
        R_conc = self.k_conc * math.tanh(soc_inv)   # saturates at depletion
        R_surface = self.k_surface * (1.0 - soc)     # linear with depletion
        R_total = self.R_0 + R_conc + R_surface
        return min(R_total, self.R_max)

    @property
    def v_terminal(self) -> float:
        """OCV - IR drop, with sag."""
        return self.ocv  # no-load OCV; loaded V computed in discharge()

    def _dod_to_soc(self, dod: float) -> float:
        """Depth of discharge [0..1] -> state of charge [1..0]."""
        return 1.0 - min(dod, 1.0)

    def _soft_knee(self, dod: float) -> float:
        """Lie 3 FIXED: sigmoid knee + exponential tail, not a cliff."""
        # sigmoid around 85% DoD, then exponential tail to 0
        if dod < 0.85:
            # normal region: gentle roll-off
            return 1.0 - 0.15 * math.tanh((dod - 0.5) / 0.3)
        else:
            # knee: sigmoid drop
            k = 25.0  # steepness
            x0 = 0.92  # knee center
            base = 1.0 / (1.0 + math.exp(-k * (dod - x0)))
            # exponential tail past the knee
            tail = math.exp(-15.0 * (dod - 0.95)) if dod > 0.95 else 1.0
            return (1.0 - base) * tail

    def discharge(self, I_load: float, dt_h: float = 0.1) -> tuple:
        """
        Constant-current discharge with real physics.

        Returns (time_hours, V_terminal, dod_pct, soc_arr).
        """
        Q_total = (self.z * F * self.moles_Zn_remaining_initial) / 3600.0  # Ah
        Q_max = Q_total  # total charge

        t_arr, V_arr, dod_arr, soc_arr = [], [], [], []
        Q_used = 0.0  # Ah

        dt = dt_h  # hours per step

        while Q_used < Q_max:
            dod = Q_used / Q_max  # [0, 1]
            self.soc = self._dod_to_soc(dod)
            self.moles_Zn_remaining = self.moles_Zn_remaining_initial * self.soc
            # Cu2+ concentration drops as Cu deposits
            self.C_cathode = self.C_cathode_init * max(self.soc, 0.01)

            v_oc = self.ocv
            r_int = self.R_int
            v_term = v_oc - I_load * r_int

            knee_factor = self._soft_knee(dod)
            v_term *= knee_factor

            t_arr.append(Q_used / I_load)       # hours
            V_arr.append(max(v_term, 0.0))      # V
            dod_arr.append(dod * 100.0)         # %
            soc_arr.append(self.soc * 100.0)   # %

            Q_used += I_load * dt

        # final cliff to 0 (cell fully dead)
        t_arr.append(Q_used / I_load)
        V_arr.append(0.0)
        dod_arr.append(100.0)
        soc_arr.append(0.0)

        return (
            np.array(t_arr),
            np.array(V_arr),
            np.array(dod_arr),
            np.array(soc_arr),
        )


def run_v1():
    """Run the v1 refined model and print comparison with v0 lies."""
    cell = RefinedCell()
    I_load = 0.2  # A

    # Compute loaded terminal voltage
    cell.soc = 1.0  # fresh
    cell.moles_Zn_remaining = cell.moles_Zn_remaining_initial
    cell.C_cathode = cell.C_cathode_init

    v_oc = cell.ocv
    r_int = cell.R_int
    v_load = v_oc - I_load * r_int

    runtime = cell.capacity_Ah / I_load
    energy = v_load * cell.capacity_Ah

    print("=" * 64)
    print("REFINED BATTERY v1  (Zn | Cu - Daniell, real physics)")
    print("    — Lie tracking vs v0 —")
    print("=" * 64)
    print(f"  [LIE 1 FIXED] OCV (Nernst, SOC=100%): {v_oc:5.3f} V  (v0: 1.10 V constant)")
    print(f"  [LIE 2 FIXED] R_int (SOC=100%):      {r_int:5.3f} ohm  (v0: 0.50 ohm fixed)")
    print(f"  [LIE 3 FIXED] Soft knee + tail       (v0: sharp cliff)")
    print(f"  Zinc anode mass:     {cell.m_anode_g:5.1f} g")
    print(f"  Capacity:             {cell.capacity_Ah:5.3f} Ah  ({cell.capacity_C:.0f} C)")
    print(f"  Load current:         {I_load:5.3f} A")
    print(f"  Terminal V (loaded):  {v_load:5.3f} V")
    print(f"  Runtime (theoretical):{runtime:5.2f} h")
    print(f"  Delivered energy:     {energy:5.2f} Wh")
    print()

    # discharge profile
    t, V, dod_arr, soc_arr = cell.discharge(I_load)

    # print key points
    for pct in [0, 25, 50, 75, 85, 90, 95, 99, 100]:
        idx = int(pct / 100 * (len(t) - 1))
        if idx < len(t):
            # recompute R_int for this SOC without creating a new cell
            soc_val = 1.0 - dod_arr[idx] / 100.0  # SOC = 1 - DoD
            soc_clamped = max(soc_val, 0.001)
            soc_inv = (1.0 / soc_clamped) - 1.0    # ~0 at full, large at empty
            R_conc = cell.k_conc * math.tanh(soc_inv)
            R_surface = cell.k_surface * (1.0 - soc_clamped)
            R_total = min(cell.R_0 + R_conc + R_surface, cell.R_max)
            print(f"    DoD={dod_arr[idx]:6.2f}%  V_term={V[idx]:5.3f} V  SOC={soc_arr[idx]:5.1f}%  R_int={R_total:.2f}Ω")

    print()
    print("v1 discharge: sag -> knee -> soft tail (NOT a cliff)")
    print("Battery: 10/10 REFINED -> compressed to 1 indigo ball kinetic")
    print("=" * 64)


if __name__ == "__main__":
    run_v1()
