#!/usr/bin/env julia
{% if prediction_success %}
{% endif %}
{% if mod or yes_str or no_str %}
{% endif %}
{% if mod %}
const MOD = {{ mod }}
{% endif %}
{% if yes_str %}
const YES = "{{ yes_str }}"
{% endif %}
{% if no_str %}
const NO = "{{ no_str }}"
{% endif %}
{% if prediction_success %}

function solve({{ formal_arguments }})
  
end
{% endif %}

function main()
    {% if prediction_success %}
    tokens = Channel{String}(32)
    Task() do
        for line in eachline(@static VERSION < v"0.6" ? STDIN : stdin)
            for token in split(chomp(line))
                put!(tokens, token)
            end
        end
        close(tokens)
    end |> schedule
    {{ input_part }}
    solve({{ actual_arguments }})
    {% else %}
    # Failed to predict input format
    {% endif %}
end

isempty(ARGS) && main()
