# naming style

single source of truth for identifier naming in this project. `tools/lint.py`
holds the same table, and `make lint`, the ci and the pre-commit hook all run it;
change this file first and the table in the lint with it. the code philemon
brought with it predates the rule, so a name that breaks it is a warning rather
than an error, and new code is held to it.

## scope

- applies to: local variables, function parameters, struct/class members, globals,
  statics.
- does not apply to: type names, function names, macros/constants (see below), or
  third-party/vendored code.

## variable prefixes by type

| type                          | prefix   | example              |
|-------------------------------|----------|----------------------|
| bool                          | `b_`     | `b_is_ready`         |
| int / int32_t / int64_t       | `i_`     | `i_frame_count`      |
| unsigned int / uint32_t, etc. | `u_`     | `u_ref_count`         |
| size_t                        | `sz_`    | `sz_buffer_len`      |
| float                         | `f_`     | `f_delta_time`       |
| double                        | `d_`     | `d_accum_time`       |
| char                          | `c_`     | `c_delimiter`        |
| std::string / char*           | `str_`   | `str_name`           |
| raw pointer (any type)        | `p_`     | `p_buffer`           |
| double pointer                | `pp_`    | `pp_node`            |
| smart pointer (unique/shared) | `sp_`    | `sp_resource`        |
| array / container             | `arr_`   | `arr_vertices`       |
| enum value / instance         | `e_`     | `e_state`            |
| struct/class instance         | *(none)* | `transform`, `mesh`  |

## scope-modifying prefixes (stack on top of the type prefix)

| scope             | prefix | example          |
|-------------------|--------|------------------|
| global variable   | `g_`   | `g_i_frame_count`|
| static variable   | `s_`   | `s_p_instance`   |
| member variable (C++ class) | `m_` | `m_f_speed` |

## types, functions, constants

- **type names** (struct/class/enum): `PascalCase`, e.g. `RigidBody`, `FrameBuffer`.
- **function names**: `snake_case`, e.g. `update_transform()`, `alloc_buffer()`.
- **macros / `#define` constants**: `UPPER_SNAKE_CASE`, e.g. `MAX_ENTITIES`.
  Exception to the lowercase-identifier rule; this is standard C/C++ practice and
  keeps macros visually distinct from real symbols.
- **`constexpr`/`const` compile-time constants**: `UPPER_SNAKE_CASE` as well, same
  reasoning as macros.

## rationale

prefix-by-type means the type of a variable is legible at the call site without
jumping to its declaration, which matches kernel-style code review habits.

## amending this file

if a project needs a type not covered here (e.g. `glm::vec3`, custom fixed-point
type), add it to the table above rather than improvising ad hoc: the lint script
only knows what's listed here.
