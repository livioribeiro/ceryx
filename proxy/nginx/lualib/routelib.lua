function string.starts(str,s) return string.sub(str,1,string.len(s))==s end
function string.ends(str,e) return e==''or string.sub(str,-string.len(e))==e end
function string.ocurrn(str,s)
  local c=0
  for s in string.gfind(str,s) do c=c+1 end
  return c
end
local P={}
function P.sort(lhs,rhs)
  local l=string.ocurrn(lhs,'/')
  local r=string.ocurrn(rhs,'/')
  if l==r then return lhs>rhs end
  return l>r
end
function P.norm(p)
  if not string.ends(p,'/') then return p..'/'
  else return p
  end
end
function P.matches(p,s)
  local np=P.norm(p)
  local ns=P.norm(s)
  return string.starts(p, ns) or np==ns
end
local _host,_path = KEYS[1],ARGV[1]
local paths,i = {},1
local routes = redis.call('keys',_host..':*')
for _,r in pairs(routes) do
  local path=string.gsub(r,_host..':','')
  if P.matches(_path,path) then paths[i]=path; i=i+1 end
end
table.sort(paths, P.sort)
if #paths==0 then
  return redis.call('get', _host)
end
return redis.call('get',_host..':'..paths[1])