/-
Contributed in 2026 by Griffin Long, with the AI agent agent-afk, as an addition to the
ShannonBounds framework of Pjotr Buys, Sven Polak and Jeroen Zuiddam (who did not write this
file). Released under Apache 2.0 license as described in the file LICENSE.
(This file: a variant of `CapCertC19.lean` for the schedule of `CertC19c.lean`.)
-/
import ShannonBounds.CertC19c
import ShannonBounds.CapC19
import ShannonBounds.Decimal

/-!
# `Theta (C19) >= 9.357203012726939`

`CertC19c.bound` is conditional on a port system whose seven families have the sizes in
`w0`.  The base system of `BaseC19` has exactly those sizes, all proved there.  Transporting
along `strongPower Cyc19 14800 ≃g strongPower G4 3700` gives the capacity bound.
-/

namespace ShannonBounds
namespace CapCertC19c

open SimpleGraph

/-- The seven families of the `C19` base system have the sizes recorded in `w0`. -/
theorem base_fam_card : ∀ a, (BaseC19.base.fam a).card = CertC19c.w0 a := by
  intro a
  cases a
  · rw [RichPortSystem.card_fam_B, BaseC19.base_N, BaseC19.base_d]; rfl
  · rw [RichPortSystem.card_fam_N, BaseC19.base_eta]; rfl
  · exact BaseC19.base_Xc_false
  · exact BaseC19.base_Xc_true
  · rw [RichPortSystem.card_fam_O, BaseC19.base_d]; rfl
  · rw [RichPortSystem.card_fam_H, BaseC19.base_d]; rfl
  · rw [RichPortSystem.card_fam_V, BaseC19.base_d]; rfl

/-- The independent set, in the `3700`-th strong power of the base graph. -/
theorem alpha_G4_ge : CertC19c.M ≤ (strongPower BaseC19.G4 3700).indepNum :=
  CertC19c.bound BaseC19.base base_fam_card

/-- `C19^(box 14800)` is the `3700`-th strong power of `C19^(box 4)`. -/
def iso14800 : strongPower BaseC19.Cyc19 14800 ≃g strongPower BaseC19.G4 3700 :=
  (strongPower_mul_iso BaseC19.Cyc19 4 3700).trans
    (strongPower_congr CapC19.G4_iso 3700).symm

/-- The independent set, in `C19^(box 14800)`. -/
theorem alpha_strongPower_ge :
    CertC19c.M ≤ (strongPower BaseC19.Cyc19 14800).indepNum := by
  rw [independenceNumber_iso iso14800]
  exact alpha_G4_ge

/-- The capacity bound, in exact root form. -/
theorem shannonCapacity_Cyc_ge :
    ((CertC19c.M : ℕ) : ℝ) ^ ((1 : ℝ) / (14800 : ℕ)) ≤ shannonCapacity BaseC19.Cyc19 := by
  calc ((CertC19c.M : ℕ) : ℝ) ^ ((1 : ℝ) / (14800 : ℕ))
      ≤ (((strongPower BaseC19.Cyc19 14800).indepNum : ℕ) : ℝ) ^ ((1 : ℝ) / (14800 : ℕ)) := by
        apply Real.rpow_le_rpow (by positivity) _ (by positivity)
        exact_mod_cast alpha_strongPower_ge
    _ ≤ shannonCapacity BaseC19.Cyc19 :=
        shannonCapacity_ge_root BaseC19.Cyc19 14800 (by norm_num)

theorem shannonCapacity_cycleGraph_ge :
    ((CertC19c.M : ℕ) : ℝ) ^ ((1 : ℝ) / (14800 : ℕ))
      ≤ shannonCapacity (SimpleGraph.cycleGraph 19) := by
  rw [← CapC19.Cyc_eq_cycleGraph]
  exact shannonCapacity_Cyc_ge

/-- **`Theta (cycleGraph 19) >= 9.357203012726939`**. -/
theorem shannonCapacity_cycleGraph_19_ge :
    (9.357203012726939 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 19) := by
  have h := shannonCapacity_cycleGraph_ge
  refine le_trans ?_ h
  rw [show ((9.357203012726939 : ℝ))
      = ((9357203012726939 : ℕ) : ℝ) / ((1000000000000000 : ℕ) : ℝ) by norm_num]
  exact Decimal.decimal_le (by norm_num) (by norm_num) (by native_decide) le_rfl

/-- The truncation is tight. -/
theorem tight :
    9357203012726939 ^ 14800 ≤ CertC19c.M * (10 ^ 15) ^ 14800 ∧
      CertC19c.M * (10 ^ 15) ^ 14800 < 9357203012726940 ^ 14800 := by
  constructor <;> native_decide

/-- Strictly improves the bound of `CapCertC19` (BPZ). -/
theorem improves : (9.357200030000796 : ℝ) < 9.357203012726939 := by norm_num


/-- Strictly improves the bound of CapCertC19b (lane L). -/
theorem improves_1 : (9.357202700233073 : ℝ) < 9.357203012726939 := by norm_num

end CapCertC19c
end ShannonBounds

#print axioms ShannonBounds.CertC19c.bound
#print axioms ShannonBounds.CapCertC19c.shannonCapacity_cycleGraph_19_ge
#print axioms ShannonBounds.CapCertC19c.tight
