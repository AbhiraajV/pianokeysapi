from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

def find_continue_reading_link(search_string):
  """
  Finds the link to the full article on Noob Notes.

  Args:
      search_string: The search query for Noob Notes.

  Returns:
      The URL of the full article or "Link not found" if not found.
  """
  url = f"https://noobnotes.net/?s={search_string}&submit=Go"
  response = requests.get(url)
  html_content = response.content

  soup = BeautifulSoup(html_content, "html.parser")

  all_links = soup.find_all("a")

  for link in all_links:
    text = link.text.strip()
    if text == "Continue reading":
      return link.get("href")
  return "Link not found"

def get_notes(html_content):
  """
  Extracts musical notes (keyboard notation) from HTML content.

  Args:
      html_content: The HTML content of the webpage.

  Returns:
      A list of extracted musical notes (keyboard notation).
  """
  soup = BeautifulSoup(html_content, "html.parser")
  notes_container = soup.find(class_='post-content')  # Assuming notes are within a specific container

  if not notes_container:
    return {"error": "Could not find notes container in the article."}

  br_tags = notes_container.find_all("br")

  # Extract text preceding each `<br>` tag (assuming keyboard notation is before)
  keyboard_notation = []
  for tag in br_tags:
    text_before_br = tag.previous_sibling.strip()  # Get text before `<br>` and remove whitespace
    if text_before_br:
      keyboard_notation.append(text_before_br.replace('\xa0', ''))

  return keyboard_notation

@app.route('/api/notes', methods=['POST'])
def extract_notes():
  """
  API endpoint to extract musical notes from a search query.

  Returns:
      JSON response containing either the extracted notes or an error message.
  """
  search_query = request.json.get('search_query')
  if not search_query:
    return jsonify({"error": "Please provide a search query in the request body."}), 400

  # Find the link to the full article
  full_article_url = find_continue_reading_link(search_query)
  if full_article_url == "Link not found":
    return jsonify({"error": "Could not find article for search query."}), 404

  # Get the HTML content of the full article
  response = requests.get(full_article_url)
  html_content = response.content

  # Extract musical notes
  notes = get_notes(html_content)

  # Return the extracted notes or error message
  return jsonify(notes)

if __name__ == '__main__':
  app.run(debug=True)
