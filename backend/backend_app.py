from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
    {"id": 3, "title": "Third post", "content": "This is the third post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Returns a list of blog posts. Optionally sorts the posts based on query parameters.

    Query parameters:
    - sort (optional): 'title' or 'content', determines by which field to sort the posts
    - direction (optional): 'asc' for ascending or 'desc' for descending order
    """
    sort_by = request.args.get('sort', None)  # Get the 'sort' query parameter
    direction = request.args.get('direction', 'asc').lower()  # Get the 'direction' query parameter (default to 'asc')

    # Validate input parameters
    if sort_by and sort_by not in ['title', 'content']:
        return jsonify({"error": "Invalid sort field. Must be 'title' or 'content'."}), 400
    if direction not in ['asc', 'desc']:
        return jsonify({"error": "Invalid direction. Must be 'asc' or 'desc'."}), 400

    # If sorting is needed
    if sort_by:
        # Sort the posts based on the 'sort' and 'direction' parameters
        reverse = True if direction == 'desc' else False
        POSTS.sort(key=lambda post: post[sort_by].lower(), reverse=reverse)

    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def create_post():
    """
    Creates a new blog post by accepting JSON data with 'title' and 'content'.
    Automatically assigns a unique 'id' to the new post.
    """
    data = request.get_json()

    # Check if title and content are provided in the request body
    if not data.get("title") or not data.get("content"):
        return jsonify({"error": "Both 'title' and 'content' are required"}), 400

    # Create a new post with a unique ID (the next available ID)
    new_post = {
        "id": max(post["id"] for post in POSTS) + 1 if POSTS else 1,
        "title": data["title"],
        "content": data["content"]
    }

    POSTS.append(new_post)

    # Return the newly created post with a 201 Created status
    return jsonify(new_post), 201


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    """
    Deletes a post with the specified ID.
    """
    post_to_delete = next((post for post in POSTS if post["id"] == id), None)

    if post_to_delete:
        POSTS.remove(post_to_delete)
        return jsonify({"message": f"Post with id {id} has been deleted successfully."})

    return jsonify({"error": "Post not found"}), 404


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    """
    Updates a blog post with the specified ID by updating 'title' and/or 'content'.
    """
    post_to_update = next((post for post in POSTS if post["id"] == id), None)

    if not post_to_update:
        return jsonify({"error": "Post not found"}), 404

    data = request.get_json()

    # Update the title and content if provided
    post_to_update["title"] = data.get("title", post_to_update["title"])
    post_to_update["content"] = data.get("content", post_to_update["content"])

    return jsonify(post_to_update)


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Searches for posts by title or content based on the query parameters.
    """
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    filtered_posts = [
        post for post in POSTS
        if (title_query in post["title"].lower() if title_query else True) and
           (content_query in post["content"].lower() if content_query else True)
    ]

    return jsonify(filtered_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
