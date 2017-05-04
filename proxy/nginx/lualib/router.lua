local container_url = ngx.var.container_url
local host = ngx.var.host
local path = ngx.var.uri
local cache = ngx.shared.ceryx

-- Setup

-- Debug Mode
local debug_mode = os.getenv("DEBUG")

-- Cache expiration time
local cache_exptime = os.getenv("CACHE_EXPTIME")
if not cache_exptime then
    cache_exptime = 60 -- 1 minute
else
    cache_exptime = tonumber(exptime)
end

-- Redis host
local redis_host = os.getenv("REDIS_HOST")
if not redis_host then
    redis_host = "127.0.0.1"
end

-- Redis port
local redis_port = os.getenv("REDIS_PORT")
if not redis_port then
    redis_port = 6379
end

-- Redis prefix
local redis_prefix = os.getenv("REDIS_PREFIX")
if not redis_prefix then redis_prefix = "ceryx" end

-- End Setup

-- Check if key exists in local cache
local res, flags = cache:get(host .. path)
if res then
    ngx.var.container_url = res
    return
end

local redis = require "resty.redis"
local red = redis:new()
red:set_timeout(100) -- 100 ms
local res, err = red:connect(redis_host, redis_port)

-- Exit if could not connect to Redis
if not res or res == ngx.null then
    ngx.log(ngx.ERR, "failed to connect to redis at " .. redis_host .. ':' .. redis_port .. ': ' .. err)
    ngx.exit(ngx.ERROR)
end

-- Prepare Redis lua script
local route_script, flags = cache:get('route_script')
if not route_script then
    -- Read routelib.lua file
    io.input('/usr/local/openresty/nginx/lualib/routelib.lua')
    server_script, err = io.read('*all')

    if err then
        ngx.log(ngx.ERR, 'failed to read redis routelib script: ' .. err)
        ngx.exit(ngx.ERROR)
    end

    route_script, err = red:script('load', server_script)

    if err then
        ngx.log(ngx.ERR, 'failed to load redis routelib script: ' .. err)
        ngx.exit(ngx.ERROR)
    end

    if not debug_mode then
        cache:set('route_script', route_script)
    end
end

-- Construct Redis key
local key = redis_prefix .. ":routes:" .. host

-- Try to get target for host
res, err = red:evalsha(route_script, 1, key, path)

-- Exit if route could not be read
if err then
    ngx.log(ngx.ERR, "error reading route: " .. err)
    ngx.exit(ngx.ERROR)
end

if not res or res == ngx.null then
    ngx.log(ngx.WARN, "no route for host: " .. host .. path)

    -- Construct Redis key for $wildcard
    key = redis_prefix .. ":routes:$wildcard"
    res, err = red:get(key)
    
    if not res or res == ngx.null then
        ngx.exit(ngx.HTTP_NOT_FOUND)
    end

    ngx.var.container_url = res[1]
    ngx.var.container_path = res[2]

    return
end

-- Save found key to local cache for specified time in seconds
if not debug_mode then
    cache:set(host, res, cache_exptime)
end

ngx.var.container_url = res[1]
ngx.var.container_path = res[2]
