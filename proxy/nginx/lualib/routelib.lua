function string.starts(String, Start)
   return string.sub(String, 1, string.len(Start)) == Start
end

function string.ends(String, End)
   return End == '' or string.sub(String, -string.len(End)) == End
end

function string.occurrencies(String, Search)
    local count = 0
    for s in string.gfind(String, Search) do
        count = count + 1
    end
    return count
end

local routepath = {}

function routepath.sort(lhs, rhs)
    local l_occur = string.occurrencies(lhs, '/')
    local r_ocurr = string.occurrencies(rhs, '/')

    if l_occur == r_ocurr then
        return lhs > rhs
    end

    return l_occur > r_ocurr
end

function routepath.normalize(path)
    if not string.ends(path, '/') then
        return path .. '/'
    else
        return path
    end
end

function routepath.starts(Path,Start)
    local norm_path = routepath.normalize(Path)
    local norm_start = routepath.normalize(Start)

    return string.starts(norm_path, norm_start)
end

local prefixed_host = KEYS[1]
local given_path = ARGV[1]

local paths = {}
local idx = 1

local routes = redis.call('keys', prefixed_host .. ':*')

for _,r in pairs(routes) do
    local path = string.gsub(r, prefixed_host .. ':', '')
    if routepath.starts(given_path, path) then
        paths[idx] = path
        idx = idx + 1
    end
end

table.sort(paths, routepath.sort)

if paths[1] == nil then
    return nil
end

return redis.call('get', prefixed_host .. ':' .. paths[1])