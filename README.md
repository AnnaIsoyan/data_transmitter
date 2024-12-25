This is an api for file transfer between two servers

STRUCTURE TREE

├───cfg
├───decorator
├───handler
├───operation
├───scheduler
├───sources
├───utils
└───var
    └───log

- Receive data from external source
- validate data, process files, save
- send to the source server data using scheduler
- send files on additional request
- send back to the external server response data received from target source

  **decorator**
- data and file validation logic

  **handler**
- loggers

  **operation**
- process data - create/update/get mongo record

  **scheduler**
- interval scheduler to send processed data to the target server

  **sources**
- post/get processors

  **utils**
- mongo manipulation logic
- file manipulation logic
