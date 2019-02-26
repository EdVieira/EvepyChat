# encoding: utf-8
import os

#DEBUG = True

# MongoDB configs

MONGO_HOST = 'localhost'
MONGO_PORT = 27017

# Skip these if your db has no auth. But it really should.
#MONGO_USERNAME = '<your username>'
#MONGO_PASSWORD = '<your password>'
#MONGO_AUTH_SOURCE = 'admin'  # needed if --auth mode is enabled

MONGO_DBNAME = 'evepychat'


# API config

RESOURCE_METHODS = ['GET','POST','DELETE']

ITEM_METHODS = ['GET','PATCH','PUT','DELETE']

EXTENDED_MEDIA_INFO = ['content_type', 'name', 'length']

DOMAIN = {
	'user':{
        'public_methods': ['POST'], # Allow non-authenticated public to create account
		'schema':{
			'image':{
				'type':'media',
			},
			'username':{
				'type':'string',
				'minlength':4,
				'required':True,
				'unique':True
			},
			'pwd':{
				'type':'string',
				'required':True,
			}
		}
	},
	'conversation':{
		'schema':{
			'image':{
				'type':'media',
			},
			'title':{
				'type':'string',
				'minlength':3,
				'required':True
			},
			'desc':{
				'type':'string',
				'minlength':3,
			},
			'adms':{
				'type':'list',
				'schema':{
					'type':'dict',
					'schema':{
						'_id':{
							'type':'objectid',
							'data_relation':{
								'resource':'user',
								'field':'_id',
								'embeddable':True
							}
						}
					}
				},
				'required':True
			},
			'users':{
				'type':'list',
				'schema':{
					'type':'dict',
					'schema':{
						'_id':{
							'type':'objectid',
							'data_relation':{
								'resource':'user',
								'field':'_id',
								'embeddable':True
							}
						}
					}
				},
				'required':True
			},
			'user':{
				'type':'objectid',
				'data_relation':{
					'resource':'user',
					'field':'_id',
					'embeddable':True
				},
				'required':True
			}
		}
	},
	'messages':{
		'schema':{
			'from':{
				'type':'objectid',
				'data_relation':{
					'resource':'user',
					'field':'_id',
					'embeddable':True
				},
				'required':True
			},
			'to':{
				'type':'objectid',
				'data_relation':{
					'resource':'conversation',
					'field':'_id',
					'embeddable':True
				},
				'required':True
			},
			'content':{
				'type':'string',
				'minlength':1,
				'maxlength':256,
				'required':True
			},
			'answerTo':{
				'type':'objectid',
				'data_relation':{
					'resource':'messages',
					'field':'_id',
					'embeddable':True
				}
			},
			'readedBy':{
				'type':'list',
				'schema':{
					'type':'dict',
					'schema':{
						'_id':{
							'type':'objectid',
							'data_relation':{
								'resource':'user',
								'field':'_id',
								'embeddable':True
							}
						}
					}
				}
			}
		}
	}
}