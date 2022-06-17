# github-bulk-editor

I needed to transfer a large bunch of repositories from one organization to another one. I had already found https://github.com/ahmadnassri/github-bulk-transfer, but that looked quite brittle, and I am honestly not a big fan of node.js projects anyway (*cough* left-pad *cough*).

So I put this tool together over the course of a couple of evenings, which allows you to:

  - fetch a list of items from the Github API - currently supported:
    - all repos the current user has permission for
    - all teams in an organization
    - all members of an organization
  - and execute an API command for a selected subset of the items - currently supported:
    - transfer repos to another organization
    - remove teams
    - remove members

![Screenshot](https://github.com/floe/github-bulk-editor/raw/master/github-bulk-editor.png "Screenshot")

To use it, you need to add your own account and access token from https://github.com/settings/tokens in line 10 (https://github.com/floe/github-bulk-editor/blob/master/github-bulk-editor.py#L10).
  
Currently, the only well-tested actions are a) fetching a list of repos you have access to, and b) transferring those repos to another user/org, because that is the functionality I needed right now.

However, I've tried to keep the internals as generic as possible (see https://github.com/floe/github-bulk-editor/blob/master/github-bulk-editor.py#L14-L27):

```python
# command title: [ GET url, JSON field to extract from result ]
fetch_cmds = { 
    "Get all repositories": [ "https://api.github.com/user/repos", "full_name"],
    "Get all teams": [ "https://api.github.com/orgs/mmbuw/teams", "slug" ], # TODO: make org name editable
    "Get all members": [ "https://api.github.com/orgs/mmbuw/members", "login" ], # TODO: make org name editable
}

# command title: [ request function, url, parameters ] (will be passed through format(name,id), hence the double braces)
action_cmds = {
    "Transfer repository": [ "github_post", "https://api.github.com/repos/{0}/transfer", '{{ "new_owner": "{0}", "team_ids": [] }}' ],
    "Delete team": [ "github_delete", "https://api.github.com/teams/{1}", "" ],
    "Remove member": [ "github_delete", "https://api.github.com/orgs/mmbuw/members/{0}", "" ], # TODO: fixed org name
}

# ...

# post a payload to url
def github_post(url,payload):
    r = requests.post(url,auth=cred,headers=headers,data=payload,allow_redirects=True)
    return r
```

In theory, you should be able to just add new entries to `fetch_cmds` and `action_cmds` to support new API calls, and perhaps add something like another `github_put` (or whatever) function.

P.S. If you're wondering why I used `requests` + `json` (as also suggested at https://stackoverflow.com/a/10626326/838719) instead of `PyGithub` or similar, none of the existing Python libraries actually support the "Transfer Repo" command. Duh.
