/-
Contributed in 2026 by Griffin Long, with the AI agent agent-afk, as an addition to the
ShannonBounds framework of Pjotr Buys, Sven Polak and Jeroen Zuiddam (who did not write this
file). Released under Apache 2.0 license as described in the file LICENSE.
(This file: a variant of `CapCertC15.lean` for the schedule of `CertC15b.lean`.)
-/
import ShannonBounds.CertC15b
import ShannonBounds.CapC15
import ShannonBounds.Decimal

/-!
# `Theta (C15) >= 7.301635000991096`

`CertC15b.bound` is conditional on a port system whose seven families have the sizes in
`w0`.  The base system of `BaseC15` has exactly those sizes, all proved there.  Transporting
along `strongPower Cyc15 3424 ≃g strongPower G4 856` gives the capacity bound.
-/

namespace ShannonBounds
namespace CapCertC15b

open SimpleGraph

/-- The seven families of the `C15` base system have the sizes recorded in `w0`. -/
theorem base_fam_card : ∀ a, (BaseC15.base.fam a).card = CertC15b.w0 a := by
  intro a
  cases a
  · rw [RichPortSystem.card_fam_B, BaseC15.base_N, BaseC15.base_d]; rfl
  · rw [RichPortSystem.card_fam_N, BaseC15.base_eta]; rfl
  · exact BaseC15.base_Xc_false
  · exact BaseC15.base_Xc_true
  · rw [RichPortSystem.card_fam_O, BaseC15.base_d]; rfl
  · rw [RichPortSystem.card_fam_H, BaseC15.base_d]; rfl
  · rw [RichPortSystem.card_fam_V, BaseC15.base_d]; rfl

/-- The independent set, in the `856`-th strong power of the base graph. -/
theorem alpha_G4_ge : CertC15b.M ≤ (strongPower BaseC15.G4 856).indepNum :=
  CertC15b.bound BaseC15.base base_fam_card

/-- `C15^(box 3424)` is the `856`-th strong power of `C15^(box 4)`. -/
def iso3424 : strongPower BaseC15.Cyc15 3424 ≃g strongPower BaseC15.G4 856 :=
  (strongPower_mul_iso BaseC15.Cyc15 4 856).trans
    (strongPower_congr CapC15.G4_iso 856).symm

/-- The independent set, in `C15^(box 3424)`. -/
theorem alpha_strongPower_ge :
    CertC15b.M ≤ (strongPower BaseC15.Cyc15 3424).indepNum := by
  rw [independenceNumber_iso iso3424]
  exact alpha_G4_ge

/-- The capacity bound, in exact root form. -/
theorem shannonCapacity_Cyc_ge :
    ((CertC15b.M : ℕ) : ℝ) ^ ((1 : ℝ) / (3424 : ℕ)) ≤ shannonCapacity BaseC15.Cyc15 := by
  calc ((CertC15b.M : ℕ) : ℝ) ^ ((1 : ℝ) / (3424 : ℕ))
      ≤ (((strongPower BaseC15.Cyc15 3424).indepNum : ℕ) : ℝ) ^ ((1 : ℝ) / (3424 : ℕ)) := by
        apply Real.rpow_le_rpow (by positivity) _ (by positivity)
        exact_mod_cast alpha_strongPower_ge
    _ ≤ shannonCapacity BaseC15.Cyc15 :=
        shannonCapacity_ge_root BaseC15.Cyc15 3424 (by norm_num)

theorem shannonCapacity_cycleGraph_ge :
    ((CertC15b.M : ℕ) : ℝ) ^ ((1 : ℝ) / (3424 : ℕ))
      ≤ shannonCapacity (SimpleGraph.cycleGraph 15) := by
  rw [← CapC15.Cyc_eq_cycleGraph]
  exact shannonCapacity_Cyc_ge

/-- **`Theta (cycleGraph 15) >= 7.301635000991096`**. -/
theorem shannonCapacity_cycleGraph_15_ge :
    (7.301635000991096 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 15) := by
  have h := shannonCapacity_cycleGraph_ge
  refine le_trans ?_ h
  rw [show ((7.301635000991096 : ℝ))
      = ((7301635000991096 : ℕ) : ℝ) / ((1000000000000000 : ℕ) : ℝ) by norm_num]
  exact Decimal.decimal_le (by norm_num) (by norm_num) (by native_decide) le_rfl

/-- The truncation is tight. -/
theorem tight :
    7301635000991096 ^ 3424 ≤ CertC15b.M * (10 ^ 15) ^ 3424 ∧
      CertC15b.M * (10 ^ 15) ^ 3424 < 7301635000991097 ^ 3424 := by
  constructor <;> native_decide

/-- Strictly improves the bound of `CapCertC15` (BPZ). -/
theorem improves : (7.301628695930103 : ℝ) < 7.301635000991096 := by norm_num

end CapCertC15b
end ShannonBounds

#print axioms ShannonBounds.CertC15b.bound
#print axioms ShannonBounds.CapCertC15b.shannonCapacity_cycleGraph_15_ge
#print axioms ShannonBounds.CapCertC15b.tight
