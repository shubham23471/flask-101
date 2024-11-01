from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

# # ingesting data to elastic
# es.index(index='my_index', id=1, document={'text': 'this is a test'})
# es.index(index='my_index', id=2, document={'text': 'a second test'})

# searching a text
# print(es.search(index='my_index', query={'match' : {'text': "this test"}}))
# print('-'*70)
# # deleting the index 
# print(es.indices.delete(index='my_index'))


print('List of all the index', es.indices.get_alias(index="*"))
# print(es.search(index='posts', query={'match' : {'text': "Post"}}))