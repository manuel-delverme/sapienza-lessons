KnowledgeBase Server
Documentation


Server coordinates:
host: 151.100.179.26
port: 8080
path: /KnowledgeBaseServer/rest-api/
Endpoints:
items_number_from
Use this endpoint to get the number of items that has an id greater or equal to the given id. The number of such items is returned as long.
Parameters:
id: the id from which you want to start count the items.
key: your access key


Example:
curl “http://151.100.179.26:8080/KnowledgeBaseServer/rest-api/items_number_from?id=0&key=X”

items_from
Use this endpoint to get the 5000 items with id greater or equal to the given id.
To retrieve more you will need to implement a pagination mechanism.
A json list of DataEntry is returned.
Parameters:
id: the lowest id you want to retrieve
key: your access key
Example:
Get the next 5000 elements:
curl “http://151.100.179.26:8080/KnowledgeBaseServer/rest-api/items_from?id=0&key=X”

Paginating:
curl “http://151.100.179.26:8080/KnowledgeBaseServer/rest-api/items_from?id=0&key=X”
last_id=get_last_id_from_list() + 1
curl “http://151.100.179.26:8080/KnowledgeBaseServer/rest-api/items_from?id=$last_id&key=X”

add_item
Use this endpoint with a post query to add an entry to the database. Will be returned 1 if the operation is successful -1 otherwise.
Parameters:
key: your access key
POST body:
The body of the post request must be a json containing a DataEntry.
Example:
curl -H "Content-Type: application/json" -X POST --data '{"question":"q","answer":"a", "relation":"size", "context":"c", "domains":"d", "c1":"c1", "c2":"c2"}' http://151.100.179.26:8080/KnowledgeBaseServer/rest-api/add_item?key=X

add_items
Use this endpoint to issue a post query to add multiple entries ad once into the database. Will be returned 1 if all the documents have been added, the list of the index of the document that couldn’t have been added due to some errors.
Parameters:
key: your access key
POST body
The body of the post reqeust must be a json containing a list of DataEntry.
Example
curl -H "Content-Type: application/json" -X POST --data '[{"question":"q","answer":"a", "relation":"size", "context":"c", "domains":"d", "c1":"c1", "c2":"c2"}, {"question":"q2","answer":"a2", "relation":"size", "context":"c2", "domains":"d2", "c1":"c1_2", "c2":"c2_2"}]' http://151.100.179.26:8080/KnowledgeBaseServer/rest-api/add_item?key=X



Exception Handling:
In any request if a ill-formed json is given as input than a bad request is returned as response status.

Testing:
If you want to test your methods to add entries please use “add_items_test” and “add_item” endpoints. They work exactly the same as “add_items” and “add_item” but do not modify the database.

FAQ:
this section will be filled during the project implementation.
