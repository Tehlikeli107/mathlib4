/-
Copyright (c) 2023 Winston Yin. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Winston Yin
-/
module Mathlib.Geometry.Manifold.IntegralCurve.ExistUnique

public import Mathlib.Analysis.ODE.Gronwall
public import Mathlib.Analysis.ODE.PicardLindelof
public import Mathlib.Geometry.Manifold.IntegralCurve.Transform
public import Mathlib.Geometry.Manifold.IsManifold.InteriorBoundary
public import Mathlib.Topology.MetricSpace.Lipschitz
public import Mathlib.Analysis.Normed.Module.FiniteDimension

/-!
# Existence and uniqueness of integral curves

## Main results

* `exists_isMIntegralCurveAt_of_contMDiffAt_boundaryless`: Existence of local integral curves for a
$C^1$ vector field. This follows from the existence theorem for solutions to ODEs
(`exists_forall_hasDerivAt_Ioo_eq_of_contDiffAt`).
* `isMIntegralCurveOn_Ioo_eqOn_of_contMDiff_boundaryless`: Uniqueness of local integral curves for a
$C^1$ vector field. This follows from the uniqueness theorem for solutions to ODEs
(`ODE_solution_unique_of_mem_set_Ioo`). This requires the manifold to be Hausdorff (`T2Space`).

## Implementation notes

For the existence and uniqueness theorems, we assume that the image of the integral curve lies in
the interior of the manifold. The case where the integral curve may lie on the boundary of the
manifold requires special treatment, and we leave it as a TODO.

We state simpler versions of the theorem for boundaryless manifolds as corollaries.

## TODO

* The case where the integral curve may venture to the boundary of the manifold. See Theorem 9.34,
  Lee. May require submanifolds.

## Reference

* [Lee, J. M. (2012). _Introduction to Smooth Manifolds_. Springer New York.][lee2012]

## Tags

integral curve, vector field, local existence, uniqueness
-/

noncomputable section

open scoped Topology

open Function Set

variable
  {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
  {H : Type*} [TopologicalSpace H] {I : ModelWithCorners ℝ E H}
  {M : Type*} [TopologicalSpace M] [ChartedSpace H M] [IsManifold I 1 M]
  {γ γ' : ℝ → M} {v : (x : M) → TangentSpace I x} {s s' : Set ℝ} (t₀ : ℝ) {x₀ : M}

/-- Existence of local integral curves for a $C^1$ vector field at interior points of a `C^1`
manifold. -/
theorem exists_isMIntegralCurveAt_of_contMDiffAt [CompleteSpace E]
    (hv : ContMDiffAt I I.tangent 1 (fun x ↦ (⟨x, v x⟩ : TangentBundle I M)) x₀)
    (hx : I.IsInteriorPoint x₀) :
    ∃ γ : ℝ → M, γ t₀ = x₀ ∧ IsMIntegralCurveAt γ v t₀ := by
  -- express the differentiability of the vector field `v` in the local chart
  rw [contMDiffAt_iff] at hv
  obtain ⟨_, hv⟩ := hv
  -- use Picard-Lindelöf theorem to extract a solution to the ODE in the local chart
  obtain ⟨f, hf1, hf2⟩ := hv.contDiffAt (range_mem_nhds_isInteriorPoint hx)
    |>.snd.exists_forall_mem_closedBall_exists_eq_forall_mem_Ioo_hasDerivAt₀ t₀
  simp_rw [← Real.ball_eq_Ioo, ← Metric.eventually_nhds_iff_ball] at hf2
  -- use continuity of `f` so that `f t` remains inside `interior (extChartAt I x₀).target`
  have ⟨a, ha, hf2'⟩ := Metric.eventually_nhds_iff_ball.mp hf2
  have hcont := (hf2' t₀ (Metric.mem_ball_self ha)).continuousAt
  rw [continuousAt_def, hf1] at hcont
  have hnhds : f ⁻¹' (interior (extChartAt I x₀).target) ∈ 𝓝 t₀ :=
    hcont _ (isOpen_interior.mem_nhds ((I.isInteriorPoint_iff).mp hx))
  rw [← eventually_mem_nhds_iff] at hnhds
  -- obtain a neighbourhood `s` so that the above conditions both hold in `s`
  obtain ⟨s, hs, haux⟩ := (hf2.and hnhds).exists_mem
  -- prove that `γ := (extChartAt I x₀).symm ∘ f` is a desired integral curve
  refine ⟨(extChartAt I x₀).symm ∘ f,
    Eq.symm (by rw [Function.comp_apply, hf1, PartialEquiv.left_inv _ (mem_extChartAt_source ..)]),
    isMIntegralCurveAt_iff.mpr ⟨s, hs, ?_⟩⟩
  intro t ht
  -- collect useful terms in convenient forms
  let xₜ : M := (extChartAt I x₀).symm (f t) -- `xₜ := γ t`
  have h : HasDerivAt f (x := t) <| fderivWithin ℝ (extChartAt I x₀ ∘ (extChartAt I xₜ).symm)
    (range I) (extChartAt I xₜ xₜ) (v xₜ) := (haux t ht).1
  rw [← tangentCoordChange_def] at h
  have hf3 := mem_preimage.mp <| mem_of_mem_nhds (haux t ht).2
  have hf3' := mem_of_mem_of_subset hf3 interior_subset
  have hft1 := mem_preimage.mp <|
    mem_of_mem_of_subset hf3' (extChartAt I x₀).target_subset_preimage_source
  have hft2 := mem_extChartAt_source (I := I) xₜ
  -- express the derivative of the integral curve in the local chart
  apply HasMFDerivAt.hasMFDerivWithinAt
  refine ⟨(continuousAt_extChartAt_symm'' hf3').comp h.continuousAt,
    HasDerivWithinAt.hasFDerivWithinAt ?_⟩
  simp only [mfld_simps, hasDerivWithinAt_univ]
  change HasDerivAt ((extChartAt I xₜ ∘ (extChartAt I x₀).symm) ∘ f) (v xₜ) t
  -- express `v (γ t)` as `D⁻¹ D (v (γ t))`, where `D` is a change of coordinates, so we can use
  -- `HasFDerivAt.comp_hasDerivAt` on `h`
  rw [← tangentCoordChange_self (I := I) (x := xₜ) (z := xₜ) (v := v xₜ) hft2,
    ← tangentCoordChange_comp (x := x₀) ⟨⟨hft2, hft1⟩, hft2⟩]
  apply HasFDerivAt.comp_hasDerivAt _ _ h
  apply HasFDerivWithinAt.hasFDerivAt (s := range I) _ <|
    mem_nhds_iff.mpr ⟨interior (extChartAt I x₀).target,
      subset_trans interior_subset (extChartAt_target_subset_range ..),
      isOpen_interior, hf3⟩
  rw [← (extChartAt I x₀).right_inv hf3']
  exact hasFDerivWithinAt_tangentCoordChange ⟨hft1, hft2⟩

/-- Existence of local integral curves for a $C^1$ vector field on a `C^1` manifold without
boundary. -/
lemma exists_isMIntegralCurveAt_of_contMDiffAt_boundaryless
    [CompleteSpace E] [BoundarylessManifold I M]
    (hv : ContMDiffAt I I.tangent 1 (fun x ↦ (⟨x, v x⟩ : TangentBundle I M)) x₀) :
    ∃ γ : ℝ → M, γ t₀ = x₀ ∧ IsMIntegralCurveAt γ v t₀ :=
  exists_isMIntegralCurveAt_of_contMDiffAt t₀ hv BoundarylessManifold.isInteriorPoint

/-- Existence of local integral curves for a $C^1$ vector field at any point of a finite dimensional
`C^1` manifold. -/
theorem exists_isMIntegralCurveWithinAt_of_contMDiffAt [FiniteDimensional ℝ E]
    (hv : ContMDiffAt I I.tangent 1 (fun x ↦ (⟨x, v x⟩ : TangentBundle I M)) x₀) :
    ∃ γ : ℝ → M, ∃ s : Set ℝ, t₀ ∈ s ∧ IsMIntegralCurveWithinAt γ v s t₀ := by
  -- extract local representative
  rw [contMDiffAt_iff] at hv
  obtain ⟨u, hu, hv⟩ := hv
  rcases mem_nhds_iff.mp hu with ⟨U, hUu, hU, hx0⟩
  let x_chart := extChartAt I x₀ x₀
  obtain ⟨r, hr, hball⟩ : ∃ r > 0, Metric.closedBall x_chart r ⊆ U :=
    Metric.nhds_basis_closedBall.mem_iff.mp (hU.mem_nhds hx0)
  let f := (fun x ↦ tangentCoordChange I ((extChartAt I x₀).symm x) x₀ ((extChartAt I x₀).symm x)
    (v ((extChartAt I x₀).symm x)))
  let s_lip := range I ∩ Metric.closedBall x_chart r
  have hconvex : Convex ℝ s_lip := (I.convex_range).inter (Metric.convex_closedBall _ _)
  have hbounded : Metric.IsBounded s_lip := Metric.isBounded_closedBall.subset inter_subset_right
  have hcont : ContDiffOn ℝ 1 f s_lip := by
    apply hv.mono
    intro x hx
    exact ⟨hx.1, hball hx.2⟩
  obtain ⟨K, hK_lip⟩ := hcont.exists_lipschitzOnWith hconvex hbounded
  -- extend f from s_lip to E
  let iso := (Module.Finite.finBasis ℝ E).equivFun
  let K_iso := ‖(iso : E →L[ℝ] (Fin (Module.Finite.finBasis ℝ E).index.card → ℝ))‖₊
  let K_pi := K_iso * K
  have hf_pi_lip : LipschitzOnWith K_pi (iso ∘ f) s_lip :=
    LipschitzOnWith.comp iso.lipschitz.lipschitzOnWith hK_lip subset_rfl
  obtain ⟨g_pi, hg_pi_lip, hg_pi_eq⟩ := LipschitzOnWith.extend_pi hf_pi_lip
  let g := iso.symm ∘ g_pi
  let K_symm := ‖(iso.symm : _ →L[ℝ] E)‖₊
  let K_g := K_symm * K_pi
  have hg_lip : LipschitzWith K_g g :=
    LipschitzWith.comp iso.symm.lipschitz.lipschitzWith hg_pi_lip
  have hg_eq (x : E) (hx : x ∈ s_lip) : g x = f x := by
    simp only [g, Function.comp_apply]
    rw [hg_pi_eq hx, iso.symm_apply_apply]
  obtain ⟨C, hC⟩ : ∃ C, ∀ x ∈ Metric.closedBall x_chart r, ‖g x‖ ≤ C := by
    have : ContinuousOn g (Metric.closedBall x_chart r) := hg_lip.continuous.continuousOn
    exact this.bounded_image Metric.isBounded_closedBall |>.exists_norm_le
  let L := K_g
  let ε := r / (C + 1)
  have hε : 0 < ε := div_pos hr (add_pos_of_nonneg_of_pos (norm_nonneg _) zero_lt_one)
  have h_picard : IsPicardLindelof (fun _ _ ↦ g) ⟨t₀, le_rfl, le_rfl⟩ x_chart r 0 C L :=
    IsPicardLindelof.of_time_independent (fun x hx ↦ hC x hx) (hg_lip.lipschitzOnWith _)
      (by
        rw [sub_zero]
        refine le_trans (mul_le_mul_of_nonneg_left ?_ (L.2)) ?_
        · rw [max_comm, max_eq_left (sub_le_self _ (le_of_lt hε))]
          simp only [tsub_le_iff_right, le_add_iff_nonneg_right, abs_nonneg]
          rw [div_mul_eq_mul_div, mul_comm, ← div_mul_eq_mul_div]
          apply div_le_of_nonneg_of_le_mul (by positivity) (by positivity)
          rw [mul_add, mul_one]
          apply add_le_add_left
          exact le_mul_of_one_le_right (le_of_lt hr) (norm_nonneg _)
        · exact le_rfl)
  obtain ⟨α, hα⟩ := ODE.FunSpace.exists_isFixedPt_next h_picard (Metric.mem_closedBall_self (le_of_lt hr))
  let γ_E := α.compProj
  let s := { t ∈ Icc (t₀ - ε) (t₀ + ε) | γ_E t ∈ range I }
  refine ⟨(extChartAt I x₀).symm ∘ γ_E, s, ?_⟩
  have ht0_s : t₀ ∈ s := by
    simp [s, hε.le]
    rw [ODE.FunSpace.compProj_val, ← hα, ODE.FunSpace.next_apply₀]
    exact mem_extChartAt_source .. ▸ mem_range_self _
  constructor
  · exact ht0_s
  rw [IsMIntegralCurveWithinAt, Filter.eventually_nhdsWithin_iff]
  filter_upwards [self_mem_nhdsWithin]
  intro t ht
  rcases ht with ⟨ht_icc, ht_range⟩
  have h_deriv_E : HasDerivWithinAt γ_E (g (γ_E t)) (Icc (t₀ - ε) (t₀ + ε)) t := by
    apply ODE.hasDerivWithinAt_picard_Icc (x₀ := x_chart) (t := t) (tmin := t₀ - ε) (tmax := t₀ + ε)
    · simp [hε.le]
    · exact h_picard.continuousOn_uncurry
    · exact α.continuous_compProj.continuousOn
    · intro t ht
      exact α.compProj_mem_closedBall h_picard.mul_max_le
    · exact ht_icc
  have h_mem_ball : γ_E t ∈ Metric.closedBall x_chart r :=
    α.compProj_mem_closedBall h_picard.mul_max_le
  have h_eq_f : g (γ_E t) = f (γ_E t) := hg_eq _ ⟨ht_range, h_mem_ball⟩
  rw [h_eq_f] at h_deriv_E
  let xₜ : M := (extChartAt I x₀).symm (γ_E t)
  -- Transform derivative to chart at xₜ
  rw [HasMFDerivWithinAt, hasMFDerivWithinAt_iff_hasFDerivWithinAt]
  -- We need HasFDerivWithinAt (extChartAt I xₜ ∘ (extChartAt I x₀).symm ∘ γ_E) (v xₜ) s t
  -- We have HasFDerivWithinAt γ_E (f (γ_E t)) s t
  -- We use chain rule.
  let ψ := extChartAt I x₀
  let ψ' := extChartAt I xₜ
  -- Note: xₜ = ψ.symm (γ_E t)
  -- We want D(ψ' ∘ ψ.symm) (γ_E t) (f (γ_E t)) = v xₜ
  have h_trans : HasFDerivWithinAt (ψ' ∘ ψ.symm) (v xₜ) (range I) (γ_E t) := by
    rw [hasFDerivWithinAt_iff_hasFDerivAt_of_mem_interior]
    · rw [← tangentCoordChange_def]
      rw [tangentCoordChange_comp (y := x₀)]
      · rw [tangentCoordChange_self]
        · simp only [ContinuousLinearMap.one_comp, xₜ, ψ, ψ']
        · exact mem_extChartAt_source ..
      · exact ⟨mem_extChartAt_source .., mem_extChartAt_source ..⟩
      · simp only [Function.comp_apply, PartialHomeomorph.left_inv, xₜ, ψ, ψ']
    · apply (hasFDerivWithinAt_tangentCoordChange ⟨mem_extChartAt_source .., mem_extChartAt_source ..⟩).congr
      · intro y hy; rfl
      · rfl
  refine HasFDerivWithinAt.comp _ h_trans (h_deriv_E.mono (sep_subset _ _)) ?_
  · apply mapsTo_image

variable {t₀}

/-- Local integral curves are unique.

If a $C^1$ vector field `v` admits two local integral curves `γ γ' : ℝ → M` at `t₀` with
`γ t₀ = γ' t₀`, then `γ` and `γ'` agree on some open interval containing `t₀`. -/
theorem isMIntegralCurveAt_eventuallyEq_of_contMDiffAt (hγt₀ : I.IsInteriorPoint (γ t₀))
    (hv : ContMDiffAt I I.tangent 1 (fun x ↦ (⟨x, v x⟩ : TangentBundle I M)) (γ t₀))
    (hγ : IsMIntegralCurveAt γ v t₀) (hγ' : IsMIntegralCurveAt γ' v t₀) (h : γ t₀ = γ' t₀) :
    γ =ᶠ[𝓝 t₀] γ' := by
  -- first define `v'` as the vector field expressed in the local chart around `γ t₀`
  -- this is basically what the function looks like when `hv` is unfolded
  set v' : E → E := fun x ↦
    tangentCoordChange I ((extChartAt I (γ t₀)).symm x) (γ t₀) ((extChartAt I (γ t₀)).symm x)
      (v ((extChartAt I (γ t₀)).symm x)) with hv'
  -- extract a set `s` on which `v'` is Lipschitz
  rw [contMDiffAt_iff] at hv
  obtain ⟨_, hv⟩ := hv
  obtain ⟨K, s, hs, hlip⟩ : ∃ K, ∃ s ∈ 𝓝 _, LipschitzOnWith K v' s :=
    (hv.contDiffAt (range_mem_nhds_isInteriorPoint hγt₀)).snd.exists_lipschitzOnWith
  have hlip (t : ℝ) : LipschitzOnWith K ((fun _ ↦ v') t) ((fun _ ↦ s) t) := hlip
  -- internal lemmas to reduce code duplication
  have hsrc {g} (hg : IsMIntegralCurveAt g v t₀) :
    ∀ᶠ t in 𝓝 t₀, g ⁻¹' (extChartAt I (g t₀)).source ∈ 𝓝 t := eventually_mem_nhds_iff.mpr <|
      continuousAt_def.mp hg.continuousAt _ <| extChartAt_source_mem_nhds (g t₀)
  have hmem {g : ℝ → M} {t} (ht : g ⁻¹' (extChartAt I (g t₀)).source ∈ 𝓝 t) :
    g t ∈ (extChartAt I (g t₀)).source := mem_preimage.mp <| mem_of_mem_nhds ht
  have hdrv {g} (hg : IsMIntegralCurveAt g v t₀) (h' : γ t₀ = g t₀) : ∀ᶠ t in 𝓝 t₀,
      HasDerivAt ((extChartAt I (g t₀)) ∘ g) ((fun _ ↦ v') t (((extChartAt I (g t₀)) ∘ g) t)) t ∧
      ((extChartAt I (g t₀)) ∘ g) t ∈ (fun _ ↦ s) t := by
    apply Filter.Eventually.and
    · apply (hsrc hg |>.and hg.eventually_hasDerivAt).mono
      rintro t ⟨ht1, ht2⟩
      rw [hv', h']
      apply ht2.congr_deriv
      congr <;>
      rw [Function.comp_apply, PartialEquiv.left_inv _ (hmem ht1)]
    · apply ((continuousAt_extChartAt (g t₀)).comp hg.continuousAt).preimage_mem_nhds
      rw [Function.comp_apply, ← h']
      exact hs
  have heq {g} (hg : IsMIntegralCurveAt g v t₀) :
    g =ᶠ[𝓝 t₀] (extChartAt I (g t₀)).symm ∘ ↑(extChartAt I (g t₀)) ∘ g := by
    apply (hsrc hg).mono
    intro t ht
    rw [Function.comp_apply, Function.comp_apply, PartialEquiv.left_inv _ (hmem ht)]
  -- main proof
  suffices (extChartAt I (γ t₀)) ∘ γ =ᶠ[𝓝 t₀] (extChartAt I (γ' t₀)) ∘ γ' from
    (heq hγ).trans <| (this.fun_comp (extChartAt I (γ t₀)).symm).trans (h ▸ (heq hγ').symm)
  exact ODE_solution_unique_of_eventually (.of_forall hlip)
    (hdrv hγ rfl) (hdrv hγ' h) (by rw [Function.comp_apply, Function.comp_apply, h])

theorem isMIntegralCurveAt_eventuallyEq_of_contMDiffAt_boundaryless [BoundarylessManifold I M]
    (hv : ContMDiffAt I I.tangent 1 (fun x ↦ (⟨x, v x⟩ : TangentBundle I M)) (γ t₀))
    (hγ : IsMIntegralCurveAt γ v t₀) (hγ' : IsMIntegralCurveAt γ' v t₀) (h : γ t₀ = γ' t₀) :
    γ =ᶠ[𝓝 t₀] γ' :=
  isMIntegralCurveAt_eventuallyEq_of_contMDiffAt BoundarylessManifold.isInteriorPoint hv hγ hγ' h

variable [T2Space M] {a b : ℝ}

/-- Integral curves are unique on open intervals.

If a $C^1$ vector field `v` admits two integral curves `γ γ' : ℝ → M` on some open interval
`Ioo a b`, and `γ t₀ = γ' t₀` for some `t ∈ Ioo a b`, then `γ` and `γ'` agree on `Ioo a b`. -/
theorem isMIntegralCurveOn_Ioo_eqOn_of_contMDiff (ht₀ : t₀ ∈ Ioo a b)
    (hγt : ∀ t ∈ Ioo a b, I.IsInteriorPoint (γ t))
    (hv : ContMDiff I I.tangent 1 (fun x ↦ (⟨x, v x⟩ : TangentBundle I M)))
    (hγ : IsMIntegralCurveOn γ v (Ioo a b)) (hγ' : IsMIntegralCurveOn γ' v (Ioo a b))
    (h : γ t₀ = γ' t₀) : EqOn γ γ' (Ioo a b) := by
  set s := {t | γ t = γ' t} ∩ Ioo a b with hs
  -- since `Ioo a b` is connected, we get `s = Ioo a b` by showing that `s` is clopen in `Ioo a b`
  -- in the subtype topology (`s` is also non-empty by assumption)
  -- here we use a slightly weaker alternative theorem
  suffices hsub : Ioo a b ⊆ s from fun t ht ↦ mem_setOf.mp ((subset_def ▸ hsub) t ht).1
  apply isPreconnected_Ioo.subset_of_closure_inter_subset (s := Ioo a b) (u := s) _
    ⟨t₀, ⟨ht₀, ⟨h, ht₀⟩⟩⟩
  · -- is this really the most convenient way to pass to subtype topology?
    -- TODO: shorten this when better API around subtype topology exists
    rw [hs, inter_comm, ← Subtype.image_preimage_val, inter_comm, ← Subtype.image_preimage_val,
      image_subset_image_iff Subtype.val_injective, preimage_setOf_eq]
    intro t ht
    rw [mem_preimage, ← closure_subtype] at ht
    revert ht t
    apply IsClosed.closure_subset (isClosed_eq _ _)
    · rw [continuous_iff_continuousAt]
      rintro ⟨_, ht⟩
      apply ContinuousAt.comp _ continuousAt_subtype_val
      rw [Subtype.coe_mk]
      exact hγ.continuousWithinAt ht |>.continuousAt (Ioo_mem_nhds ht.1 ht.2)
    · rw [continuous_iff_continuousAt]
      rintro ⟨_, ht⟩
      apply ContinuousAt.comp _ continuousAt_subtype_val
      rw [Subtype.coe_mk]
      exact hγ'.continuousWithinAt ht |>.continuousAt (Ioo_mem_nhds ht.1 ht.2)
  · rw [isOpen_iff_mem_nhds]
    intro t₁ ht₁
    have hmem := Ioo_mem_nhds ht₁.2.1 ht₁.2.2
    have heq : γ =ᶠ[𝓝 t₁] γ' := isMIntegralCurveAt_eventuallyEq_of_contMDiffAt
      (hγt _ ht₁.2) hv.contMDiffAt (hγ.isMIntegralCurveAt hmem) (hγ'.isMIntegralCurveAt hmem) ht₁.1
    apply (heq.and hmem).mono
    exact fun _ ht ↦ ht

theorem isMIntegralCurveOn_Ioo_eqOn_of_contMDiff_boundaryless [BoundarylessManifold I M]
    (ht₀ : t₀ ∈ Ioo a b)
    (hv : ContMDiff I I.tangent 1 (fun x ↦ (⟨x, v x⟩ : TangentBundle I M)))
    (hγ : IsMIntegralCurveOn γ v (Ioo a b)) (hγ' : IsMIntegralCurveOn γ' v (Ioo a b))
    (h : γ t₀ = γ' t₀) : EqOn γ γ' (Ioo a b) :=
  isMIntegralCurveOn_Ioo_eqOn_of_contMDiff
    ht₀ (fun _ _ ↦ BoundarylessManifold.isInteriorPoint) hv hγ hγ' h

/-- Global integral curves are unique.

If a continuously differentiable vector field `v` admits two global integral curves
`γ γ' : ℝ → M`, and `γ t₀ = γ' t₀` for some `t₀`, then `γ` and `γ'` are equal. -/
theorem isMIntegralCurve_eq_of_contMDiff (hγt : ∀ t, I.IsInteriorPoint (γ t))
    (hv : ContMDiff I I.tangent 1 (fun x ↦ (⟨x, v x⟩ : TangentBundle I M)))
    (hγ : IsMIntegralCurve γ v) (hγ' : IsMIntegralCurve γ' v) (h : γ t₀ = γ' t₀) : γ = γ' := by
  ext t
  obtain ⟨T, ht₀, ht⟩ : ∃ T, t ∈ Ioo (-T) T ∧ t₀ ∈ Ioo (-T) T := by
    obtain ⟨T, hT₁, hT₂⟩ := exists_abs_lt t
    obtain ⟨hT₂, hT₃⟩ := abs_lt.mp hT₂
    obtain ⟨S, hS₁, hS₂⟩ := exists_abs_lt t₀
    obtain ⟨hS₂, hS₃⟩ := abs_lt.mp hS₂
    exact ⟨T + S, by constructor <;> constructor <;> linarith⟩
  exact isMIntegralCurveOn_Ioo_eqOn_of_contMDiff ht (fun t _ ↦ hγt t) hv
    ((hγ.isMIntegralCurveOn _).mono (subset_univ _))
    ((hγ'.isMIntegralCurveOn _).mono (subset_univ _)) h ht₀

theorem isMIntegralCurve_Ioo_eq_of_contMDiff_boundaryless [BoundarylessManifold I M]
    (hv : ContMDiff I I.tangent 1 (fun x ↦ (⟨x, v x⟩ : TangentBundle I M)))
    (hγ : IsMIntegralCurve γ v) (hγ' : IsMIntegralCurve γ' v) (h : γ t₀ = γ' t₀) : γ = γ' :=
  isMIntegralCurve_eq_of_contMDiff (fun _ ↦ BoundarylessManifold.isInteriorPoint) hv hγ hγ' h

/-- For a global integral curve `γ`, if it crosses itself at `a b : ℝ`, then it is periodic with
period `a - b`. -/
lemma IsMIntegralCurve.periodic_of_eq [BoundarylessManifold I M]
    (hγ : IsMIntegralCurve γ v)
    (hv : ContMDiff I I.tangent 1 (fun x ↦ (⟨x, v x⟩ : TangentBundle I M)))
    (heq : γ a = γ b) : Periodic γ (a - b) := by
  apply congrFun <|
    isMIntegralCurve_Ioo_eq_of_contMDiff_boundaryless (t₀ := b) hv (hγ.comp_add _) hγ _
  rw [comp_apply, add_sub_cancel, heq]

set_option backward.isDefEq.respectTransparency false in
/-- A global integral curve is injective xor periodic with positive period. -/
lemma IsMIntegralCurve.periodic_xor_injective [BoundarylessManifold I M]
    (hγ : IsMIntegralCurve γ v)
    (hv : ContMDiff I I.tangent 1 (fun x ↦ (⟨x, v x⟩ : TangentBundle I M))) :
    Xor' (∃ T > 0, Periodic γ T) (Injective γ) := by
  rw [xor_iff_iff_not]
  refine ⟨fun ⟨T, hT, hf⟩ ↦ hf.not_injective (ne_of_gt hT), ?_⟩
  intro h
  rw [Injective] at h
  push_neg at h
  obtain ⟨a, b, heq, hne⟩ := h
  refine ⟨|a - b|, ?_, ?_⟩
  · rw [gt_iff_lt, abs_pos, sub_ne_zero]
    exact hne
  · by_cases! hab : a - b < 0
    · rw [abs_of_neg hab, neg_sub]
      exact hγ.periodic_of_eq hv heq.symm
    · rw [abs_of_nonneg hab]
      exact hγ.periodic_of_eq hv heq
