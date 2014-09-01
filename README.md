## Sinch authentication token backend example

This demonstrates a basic partner backend for generating authentication tokens. 
In this example the user database is not persistent: Only for demonstrational purpose!
See rows ~100-120 for code on generating a Sinch compatible authentication token.


### Requirements
Python >= 2.7.X | >= 3.X
Tornado >= 4.0.1
pip (python package index)


### Installation & start
pip install tornado (or upgrade)
./backend-example.py

Default port is 2048


### Usage
The demo backend expose two resources
/register - Register user
/login - Authentication as user

Send a JSON object to either of these resources to either register a user or authenticate as a user.

Example JSON object: {username: 'someUserName', password: 'highlySecurePwd'}

Note: You can't authenticate as a user before it's registered!


### Example in Javascript

```javascript
<script>
	var loginObj = JSON.stringify({'username': 'magnus', 'password': 'superSecure'});

	$.post('http://localhost:2048/login', loginObj, {}, "json")
		.done(function(authTicket) {

			sinchClient2.start(authTicket)
				.then(function() {
					console.log('SUCCESS!');
				})
				.fail(function(error) {
					console.error('SinchClient fail!');
				})
				.done();
		})
		.fail(function(error) {
			console.error('Auth failure!');
		});
</script>
```


