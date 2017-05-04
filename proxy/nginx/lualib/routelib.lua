function string.starts(input, search)
    return string.sub(input, 1, string.len(search)) == search
end

function string.ends(input, search)
    return search == '' or string.sub(input, -string.len(search)) == search
end

function string.ocurrencies(input, search)
    local count = 0
    for s in string.gfind(input, search) do
        count = count + 1
    end
    return count
end

-- namespace for path related functions
local Path = {}

function Path.sort(lhs, rhs)
    local l_ocurr = string.ocurrencies(lhs, '/')
    local r_ocurr = string.ocurrencies(rhs, '/')
    if l_ocurr == r_ocurr then
        return lhs > rhs
    end
    return l_ocurr > r_ocurr
end

-- normalize path by adding a trailing '/' if needed
function Path.normalize(path)
    if not string.ends(path, '/') then
        return path .. '/'
    else
        return path
    end
end

function Path.matches(path, search)
    local npath = Path.normalize(path)
    local nsearch = Path.normalize(search)
    return string.starts(path, nsearch) or npath == nsearch
end

local arg_host, arg_path = KEYS[1], ARGV[1]
local paths = {}
local idx = 1

local routes = redis.call('keys', arg_host .. ':*')

for _, route in pairs(routes) do
    local path = string.sub(route, string.len(arg_host .. ':') + 1)
    if Path.matches(arg_path, path) then
        paths[idx] = path
        idx = idx + 1
    end
end

table.sort(paths, Path.sort)

if #paths == 0 then
  return redis.call('get', arg_host)
end

local new_path = ''
if arg_path ~= paths[1] then
    new_path = string.sub(arg_path, string.len(paths[1]) + 1)
end
if string.sub(new_path, 1, 1) ~= '/' then
    new_path = '/' .. new_path
end

return {
    redis.call('get', arg_host .. ':' .. paths[1]),
    new_path
}