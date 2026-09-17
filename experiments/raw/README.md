# Raw experiment logs

Start recording from Day 0. Analysis lives in `../results/`.

Minimum fields per task:

```text
task_id
start_time
end_time
method = manual / cursor / platform
build_failures
runtime_failures
human_interventions
llm_iterations
final_status
notes
```

Do not commit generated payloads from `../tmp/`.
