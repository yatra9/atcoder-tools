#!/usr/bin/env -S JULIA_VERSION={{ julia_version }} julia
{% if contest_id and problem_id and problem_alphabet %}
# contest: {{ contest_id }}, problem: {{ problem_id}}, alphabet: {{ problem_alphabet }}
{% endif %}
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
        function test(sampleids...)
            isempty(sampleids) && return test(collect(1:length(samples))...)
            ostdin, ostdout = @static VERSION < v"0.6" ? (STDIN, STDOUT) : (stdin, stdout)
            rd, wr = first(redirect_stdout()), last(redirect_stdin())
            try
                map(sampleids) do sampleid
                    input, output = samples[sampleid]
                    print(ostdout, "Testing sample #$(sampleid)..."); flush(ostdout)
                    println(wr, input)
                    println(wr, "\0")
                    t = @elapsed main()
                    println()
                    result = strip(String(readavailable(rd)))
                    if result == output
                        println(ostdout, "OK ($t sec).")
                    else
                        println(ostdout, "ERROR ($t sec)")
                        println(ostdout, "== expected ==\n$output")
                        println(ostdout, "== actual ==\n$result\n")
                    end
                end |> all
            catch
                exit(100)
            finally
                redirect_stdin(ostdin)
                redirect_stdout(ostdout)
            end
        end
        submit() = test() && run(`atcoder-submit @__FILE__`)
        !isinteractive() && submit()
    end
end
