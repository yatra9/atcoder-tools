#!/usr/bin/env julia
const MOD = 123
const YES = "yes"
const NO = "NO"

function solve(N::Int, M::Int, H::Matrix{String}, A::Vector{Int}, B::Vector{Float64}, Q::Int, X::Vector{Int})
  
end

# Generated by x.y.z https://github.com/kyuridenamida/atcoder-tools  (tips: You use the default template now. You can remove this line by using your custom template)
function main()
    tokens = Channel{String}(32)
    Task() do
        for line in eachline(@static VERSION < v"0.6" ? STDIN : stdin)
            for token in split(chomp(line))
                put!(tokens, token)
            end
        end
        close(tokens)
    end |> schedule
    N = parse(Int, take!(tokens))
    M = parse(Int, take!(tokens))
    H = similar(Matrix{String}, N-2+1, M-1-2+1)
    for i in 1:(N-2+1)
        for j in 1:(M-1-2+1)
            H[i,j] = take!(tokens)
        end
    end
    A = similar(Vector{Int}, N-2+1)
    B = similar(Vector{Float64}, N-2+1)
    for i in 1:(N-2+1)
        A[i] = parse(Int, take!(tokens))
        B[i] = parse(Float64, take!(tokens))
    end
    Q = parse(Int, take!(tokens))
    X = similar(Vector{Int}, M+Q)
    for i in 1:(M+Q)
        X[i] = parse(Int, take!(tokens))
    end
    solve(N, M, H, A, B, Q, X)
end

isempty(ARGS) && main()
