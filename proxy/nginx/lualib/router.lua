local container_url = ngx.var.container_url
local host = ngx.var.host
-- nginx $uri contains the request path in this context
local path = ngx.var.uri

-- Check if key exists in local cache
local cache = ngx.shared.ceryx
local res, flags = cache:get(host .. path)
if res then
    ngx.var.container_url = res
    return
end

local redis = require "resty.redis"
local red = redis:new()
red:set_timeout(100) -- 100 ms
local redis_host = os.getenv("CERYX_REDIS_HOST")
if not redis_host then redis_host = "127.0.0.1" end
local redis_port = os.getenv("CERYX_REDIS_PORT")
if not redis_port then redis_port = 6379 end
local res, err = red:connect(redis_host, redis_port)

-- Exit if could not connect to Redis
if not res then
    ngx.log(ngx.ERR, "failed to connect to redis: " .. err)
    ngx.exit(ngx.ERROR)
end

-- Setup redis script
local redis_script, flags = cache:get('redis_script')
if not redis_script then
    -- Read routelib.lua file
    io.input('/usr/local/openresty/nginx/lualib/routelib.lua')
    routelib = io.read('*all')

    -- Flush Redis scripts
    red:script('flush')

    -- Load script into Redis
    hash, err = red:script('load', routelib)

    if err then
        ngx.log(ngx.ERR, "failed to load script into redis: " .. err)
        ngx.exit(ngx.ERROR)
    end

    cache:set('redis_script', routelib)
end

-- Construct Redis key
local prefix = os.getenv("CERYX_REDIS_PREFIX")
if not prefix then prefix = "ceryx" end
local key = prefix .. ":routes:" .. host

-- Try to get target for host
res, err = red:eval(redis_script, 1, key, path)

-- Exit if route could not be read
if err then
    ngx.log(ngx.ERR, "error reading route: " .. err)
    ngx.exit(ngx.ERROR)
end

if not res or res == ngx.null then
    ngx.log(ngx.WARN, "no route for host: " .. host)

    -- Construct Redis key for $wildcard
    key = prefix .. ":routes:$wildcard"
    res, err = red:get(key)
    if not res or res == ngx.null then
        ngx.exit(ngx.HTTP_NOT_FOUND)
    end
    ngx.var.container_url = res
    return
end

-- Save found key to local cache for specified time in seconds
local exptime = os.getenv("CERYX_CACHE_EXPTIME")
if not exptime then
    exptime = 60 -- 1 minute
else
    exptime = tonumber(exptime)
end
cache:set(host, res, 5)

ngx.var.container_url = res
