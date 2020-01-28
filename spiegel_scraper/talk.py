from collections import defaultdict

import requests

from spiegel_scraper.constants import TALK_ENDPOINT_URL


def comments_by_article_id(article_id: str, page_size_limit: int = 1000):
    query = """
        query GetComments($assetId: ID!, $cursor: Cursor, $limit: Int) { 
          asset(id: $assetId) {
            comments(deep: true, query: {sortBy: CREATED_AT, sortOrder: ASC, limit: $limit, cursor: $cursor}) {
              endCursor
              hasNextPage
              nodes {
                id
                parent {id}
                body
                tags {
                  tag {
                    name
                    created_at
                  }
                  assigned_by {
                    id
                    username
                    role
                  }
                }
                user {
                  id
                  username
                  role
                }
                status
                created_at
                updated_at
                editing {
                  edited
                }
                richTextBody
                highlights {
                  start
                  end
                }
              }
            }
          }
        }
    """

    # fetch all comments into flat array
    comments = []
    cursor = None
    while True:
        resp = requests.post(TALK_ENDPOINT_URL, json={'query': query, 'variables': {
            'assetId': article_id,
            'cursor': cursor,
            'limit': page_size_limit,
        }})

        data = resp.json()['data']
        comments_data = data['asset']['comments']
        comments.extend(comments_data['nodes'])
        cursor = comments_data['endCursor']
        if not comments_data['hasNextPage']:
            break

    # build nested reply structure
    root_comments = []
    replies_by_id = defaultdict(list)
    for comment in comments:
        comment['replies'] = replies_by_id[comment['id']]
        parent_ref = comment.pop('parent')
        if parent_ref is None:
            root_comments.append(comment)
        else:
            replies_by_id[parent_ref['id']].append(comment)

    return root_comments
