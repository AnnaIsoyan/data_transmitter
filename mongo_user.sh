#!/bin/bash
NEW_USERNAME='my_superuser'
NEW_PASSWORD='qwerty'
   
CREATE_USER_CMD="db.createUser({ user: '$NEW_USERNAME', pwd: '$NEW_PASSWORD', roles: [{ role: 'userAdminAnyDatabase', db: 'admin' }] })"
mongosh --eval "$CREATE_USER_CMD"