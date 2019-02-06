# github-bulk-editor

I needed to transfer a large bunch of repositories from one organization to another one. I had already found https://github.com/ahmadnassri/github-bulk-transfer, but that looked quite brittle, and I am honestly not a big fan of node.js projects anyway (*cough* left-pad *cough*).

So I put this tool together over the course of a couple of evenings, which allows you to:

  - fetch a list of items from the Github API (**)
  - select a subset of items from the result list
  - and execute an API command for each of the selected items, with optional parameters (**) 
  
To use it, you need to add your own account and password or API key in line 10 (https://github.com/floe/github-bulk-editor/blob/master/github-bulk-editor.py#L10).
  
Currently, the only supported actions are a) fetching a list of repos you have access to, and b) transferring those repos to another user/org, because that is the functionality I needed right now.

However, I've tried to keep the internals as generic as possible (see https://github.com/floe/github-bulk-editor/blob/master/github-bulk-editor.py#L14-L23):

```python
# command title: [ GET url, JSON field to extract from result ]
fetch_cmds = { 
    "Get all repositories": [ "https://api.github.com/user/repos", "full_name"] 
}

# command title: [ request function, url, parameters ] (will be passed through format(), hence the double braces)
action_cmds = {
    "Transfer repository": [ "github_post", "https://api.github.com/repos/{0}/transfer", '{{ "new_owner": "{0}", "team_ids": [] }}' ]
}

# ...

# post a payload to url
def github_post(url,payload):

    r = requests.post(url,auth=cred,headers=headers,data=payload,allow_redirects=True)
    return r
```

In theory, you should be able to just add new entries to `fetch_cmds` and `action_cmds` to support new API calls, and perhaps add something like another `github_put` (or whatever) function.

P.S. If you're wondering why I used requests + json (as also suggested at https://stackoverflow.com/a/10626326/838719) instead of PyGithub or similar, none of the existing Python libraries actually support the "Transfer Repo" command. Duh.
