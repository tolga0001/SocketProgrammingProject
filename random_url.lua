request = function()
    local random_value = math.random(0, 1000) -- Generate a random number between 0 and 1000
    return wrk.format("GET", "/" .. random_value) -- Create a dynamic path "/x"
end


