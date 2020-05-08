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
macro Y() :( println(YES); return ) end
{% endif %}
{% if no_str %}
const NO = "{{ no_str }}"
macro N() :( println(NO); return ) end
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
            startswith(line, '\0') && break
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

if isempty(get(ENV, "ATCODER_LOCAL", ""))
    isempty(ARGS) && main()
else
    @eval begin
        {{ samples }}
        sampleids = isempty(ARGS) ? collect(1:length(samples)) : map(a->parse(Int, a), ARGS)
        ostdin, ostdout = @static VERSION < v"0.6" ? (STDIN, STDOUT) : (stdin, stdout)
        rd, wr = first(redirect_stdout()), last(redirect_stdin())
        try
            for sampleid in sampleids
                input, output = samples[sampleid]
                print(ostdout, "Testing sample #$(sampleid)..."); flush(ostdout)
                println(wr, input)
                println(wr, "\0")
                println()
                t = @elapsed main()
                result = strip(String(readavailable(rd)))
                if result == output
                    println(ostdout, "OK ($t sec).")
                else
                    println(ostdout, "ERROR ($t sec)")
                    println(ostdout, "== correct amswer ==\n$output")
                    println(ostdout, "== actual ==\n$result\n")
                end
            end
        finally
            redirect_stdin(ostdin)
            redirect_stdout(ostdout)
        end
    end
end
