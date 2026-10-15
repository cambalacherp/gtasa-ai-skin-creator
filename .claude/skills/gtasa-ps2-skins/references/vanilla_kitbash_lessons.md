# Verified vanilla kitbash lessons

Read for head swaps, UV color matching or RenderWare parser debugging. Findings come from Sindaco-head / LSV2-body assets and local verification. The handoff is historical: its "sink the head into the collar" recommendation was visually rejected and superseded.

## Neck surgery

- Vanilla UV seams duplicate vertices and meshes are not manifold. Many boundary edges alone do not prove a broken seam. Compare with the source ped and inspect renders; do not force a ring walk on disconnected UV islands.
- Keeping only triangles whose three vertices are non-head deletes the mixed neck/head transition. Sinking the chin into the shirt collar hides missing geometry by removing the visible neck. Preserve cervical transition faces and fit the skull to the removed head's proportions/crown height.
- Fit only upper neck endpoints just under the donor surface. Preserve the original lower neck and weights and the donor's head/jaw weights. Do not weight the chin to the neck just to hide a gap.
- Remove source accessories crossing the cut. LSV2's bandana tail is not neck skin; its source-specific UV/color filter is not a general rule for yellow geometry in other peds.
- Corrected recipe observations: scale 1.08558; crown mesh X=0.86963618; 20 cervical transition triangles, 18 fitted endpoints; 1,080 vertices / 1,165 triangles. Do not impose these values on other pairs.
- 500–850 vertices is an art target. Strict limits in this pipeline are 1,100 vertices, 1,600 triangles, one Geometry/Atomic and four influences per vertex.

## Verified RenderWare layout

- Clump Struct is three u32 counts: `(numAtomics, numLights, numCameras)`, `(1,0,0)` for this ped. Do not copy a chunk HEADER `(type,size,version)` into a Struct PAYLOAD. The old exporter wrote `(1,12,0x1803FFFF)`: GTA Stuff then attempted to read nonexistent lights/cameras and failed at end-of-file, position 86089. A matching in-house parser/renderer had missed this; real external-reader verification caught it.
- MaterialList Struct is a u32 material count followed by signed i32 references. A new material is `-1`; reused references must point to an earlier slot. The old `(1,8)` payload is invalid; this ped uses `(1,-1)`.
- Validate chunk boundaries without silently clamping oversized payloads. Cross-check declared Clump/GeometryList counts, FrameList payload size, Atomic frame/geometry references and MaterialList references against actual content. Add negative fixtures for each exporter bug.
- Vanilla LSV2 has 33 frames: an unbound container plus 32 bone frames. The procedural legacy generator has 32 frames; its layout is not a vanilla surgery template.
- Skin indices address the HAnim node table, not Bone IDs or FrameList indices. Preserve the body's node order and inverse bind matrices together.
- Vanilla node-index-to-Bone-ID table: `[0,1,2,3,4,5,8,6,7,31,32,33,34,35,36,21,22,23,24,25,26,302,301,201,41,42,43,44,51,52,53,54]`.
- Bone IDs: Root=0, Pelvis=1, Spine=2, Spine1=3, Neck=4, Head=5, brows=6/7, Jaw=8. Attachment API IDs are a separate namespace. Root must have zero weight; Pelvis may have full weight. Resolve Root through the node table.
- Geometry header: 16 bytes, `<HBBIII>` (u16 flags, u8 UV sets, u8 padding, triangle count, vertex count, morph count). `<BBHIII>` misreads vanilla UV data; 28-byte headers shift every array.
- Geometry triangles pack `(vertex2, vertex1, material, vertex3)`; render/BinMesh order is `(vertex1, vertex2, vertex3)`. Keep winding consistent.
- Flag 0x10 enables normals; 0x08 is prelight. PC version stamp is `0x1803FFFF`.
- A D3D9 8888 TXD may have 256 palette colors baked into pixels without a PAL8 raster flag. That flag alone does not decide PS2-style validity.
- Inverse bind matrices have affine padding. Set their homogeneous last column to `[0,0,0,1]` before inversion; raw padded 4x4 matrices can appear singular.

## Coordinates, previews and process handling

- Imported mesh space here is X=up, Y=front, Z=left. Blender basis rotation `(-Z,Y,X)` preserves handedness.
- Render the exported DFF and decoded TXD, not just an intermediate mesh: serialization, UVs and palette errors must appear in the preview.
- The user's established preview preference is local Blender CLI, without image generation APIs. Save raw captures and a packed `.blend` scene.
- Blender may exit zero after a Python exception unless `--python-exit-code 1` is set. Check the completion marker and outputs, enforce a timeout and kill its process tree on failure/timeout.
- Inspect front, side, nape and a pose. The initial 1,050-vertex output passed structural checks but visibly lacked a neck.

## Skin color matching

- Project policy for every skin and every model/agent: verify and normalize exposed skin across head, neck, torso, arms and hands as part of the normal workflow, without requiring a separate request. Use the head as the default reference unless the user selects another reference or an intentional difference. Already coherent skin needs verification rather than gratuitous recoloring. Sindaco/LSV2 is one supported example of this general requirement.
- Sample clean midtone skin, excluding hair, features, deep shadows and ink. Use inspected UV material masks and multiplicative color transfer to retain shading/tattoos; do not paint a flat fill or generate replacement imagery.
- LSV2's arm island starts at row 28, not 32. Missing these rows leaves dark shoulder strips. Do not blindly widen the chest mask: the dirty white tank top has beige pixels that broad color thresholds can misclassify.
- Profiles store source dimensions, samples and UV regions. Refuse unknown pairs/dimensions rather than silently reusing another ped's coordinates.
- Protect non-skin pixels after quantization. Recomputing a global median-cut palette can shift head/clothing colors; locking the entire old palette can starve new skin tones and add noise. Reserve protected colors, allocate free palette slots to corrected skin and restore protected final pixels byte for byte. Verify the decoded TXD has at most 256 colors.
- Check head/body samples and detail retention in the exported TXD, not only pre-quantization RGB. Keep a mask and numerical audit.

## Verification and memory

- When changing binary serialization, reproduce the failure and load the rebuilt DFF/TXD in an independent consumer (such as the user's GTA Stuff viewer). A writer and parser that share assumptions can agree on an invalid stream. Preserve a viewer screenshot and hashes of the verified files; a successful viewer load still does not claim game-runtime testing.
- Rebuild after engine changes; re-render geometry/UV/TXD changes and package current artifacts. Inspect individual reports instead of trusting a suite's summary string.
- Binary structure, Blender appearance and diagnostic pose checks do not establish in-game behavior. Only an actual game run does; report the distinction.
- Canonical memory is `AGENTS.md` plus `.agents/skills/gtasa-ps2-skins/`. Regenerate script/reference/Claude mirrors and refresh the installed skill. Keep universal guidance separate from recipe measurements and historical debugging notes.
