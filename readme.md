

Create user
POST /user
``` javascript 
{
	"username":"test",
	"pwd":"test"
};
```

Create conversation
POST /conversation

```
{
	"title":"test",
	"adms":[{"_id":"5c74bdcc3804ab262c98b046"}],
	"users":[{"_id":"5c74c7a23804ab3424005db2"},{"_id":"5c74c82e3804ab349fb718b4"}],
	"user":"5c74bdcc3804ab262c98b046"
}
```

Create message
POST /message

```
{
	"from":"5c72242f3804ab200083b28b",
	"to":"5c7450be3804ab5145c38d5f",
	"content":"Hello word!"
}
```
