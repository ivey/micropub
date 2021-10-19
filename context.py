from bs4 import BeautifulSoup
from .config import TWITTER_BEARER_TOKEN
import requests
import mf2py

def get_reply_context(url, request_type):
    h_entry = None
    site_supports_webmention = False

    if request_type == "like-of" or request_type == "repost-of" or request_type == "bookmark-of" or request_type == "in-reply-to" and (url.startswith("https://") or url.startswith("http://")):
        parsed = mf2py.parse(requests.get(url).text)

        supports_webmention = requests.get("https://webmention.jamesg.blog/discover?target={}".format(url))

        if supports_webmention.status_code == 200:
            if supports_webmention.json().get("success") == True:
                site_supports_webmention = True

        domain = url.replace("https://", "").replace("http://", "").split("/")[0]

        if parsed["items"] and parsed["items"][0]["type"] == ["h-entry"]:
            h_entry = parsed["items"][0]

            if h_entry["properties"].get("author"):
                author_url = h_entry['properties']['author'][0]['properties']['url'][0] if h_entry['properties']['author'][0]['properties'].get('url') else None
                author_name = h_entry['properties']['author'][0]['properties']['name'][0] if h_entry['properties']['author'][0]['properties'].get('name') else None
                author_image = h_entry['properties']['author'][0]['properties']['photo'][0] if h_entry['properties']['author'][0]['properties'].get('photo') else None
                if author_url.startswith("/"):
                    author_url = url.split("/")[0] + "//" + domain + author_url

                if author_image.startswith("/"):
                    author_image = url.split("/")[0] + "//" + domain + author_image
            else:
                author_url = None
                author_name = None
                author_image = None

            if h_entry["properties"].get("content") and h_entry["properties"].get("content")[0].get("html"):
                post_body = h_entry["properties"]["content"][0]["html"]
                soup = BeautifulSoup(post_body, "html.parser")
                post_body = soup.text
                
                favicon = soup.find("link", rel="icon")

                if favicon and not author_image:
                    photo_url = favicon["href"]
                    if not photo_url.startswith("https://") or not photo_url.startswith("http://"):
                        author_image = "https://" + domain + photo_url
                else:
                    author_image = None

                post_body = " ".join(post_body.split(" ")[:75]) + " ..."
            elif h_entry["properties"].get("content"):
                post_body = h_entry["properties"]["content"]

                post_body = " ".join(post_body.split(" ")[:75]) + " ..."
            else:
                post_body = None

            # get p-name
            if h_entry["properties"].get("p-name"):
                p_name = h_entry["properties"]["p-name"][0]
            else:
                p_name = None

            if not author_url.startswith("https://") and not author_url.startswith("http://"):
                author_url = "https://" + author_url

            h_entry = {"author_image": author_image, "author_url": author_url, "author_name": author_name, "post_body": post_body, "p-name": p_name}

            return h_entry, site_supports_webmention
            
        h_entry = {}

        if url.startswith("https://twitter.com"):
            site_supports_webmention = False
            tweet_uid = url.strip("/").split("/")[-1]
            headers = {
                "Authorization": "Bearer {}".format(TWITTER_BEARER_TOKEN)
            }
            r = requests.get("https://api.twitter.com/2/tweets/{}?tweet.fields=author_id".format(tweet_uid), headers=headers)

            if r and r.status_code != 200:
                return {}, None

            print(r.json()["data"].keys())

            get_author = requests.get("https://api.twitter.com/2/users/{}?user.fields=url,name,profile_image_url,username".format(r.json()["data"].get("author_id")), headers=headers)

            if get_author and get_author.status_code == 200:
                photo_url = get_author.json()["data"].get("profile_image_url")
                author_name = get_author.json()["data"].get("name")
                author_url = "https://twitter.com/" + get_author.json()["data"].get("username")
            else:
                photo_url = None
                author_name = None
                author_url = None

            h_entry = {"p-name": "", "post_body": r.json()["data"].get("text"), "author_image": photo_url, "author_url": author_url, "author_name": author_name}

            return h_entry, site_supports_webmention

        try:
            soup = BeautifulSoup(requests.get(url).text, "html.parser")

            page_title = soup.find("title")

            if page_title:
                page_title = page_title.text

            # get body tag
            main_tag = soup.find("body")

            if main_tag:
                p_tag = main_tag.find("p")
                if p_tag:
                    p_tag = p_tag.text
                else:
                    p_tag = None
            else:
                p_tag = None

            if soup.select('.e-content'):
                p_tag = soup.select('.e-content')[0]

                # get first paragraph
                if p_tag:
                    p_tag = p_tag.find("p")
                    if p_tag:
                        p_tag = p_tag.text

                    p_tag = " ".join([w for w in p_tag.split(" ")[:75]]) + " ..."
                else:
                    p_tag = ""

            if soup.select('.u-photo'):
                photo_url = soup.select('.u-photo')[0]['src']
                
            favicon = soup.find("link", rel="icon")

            if favicon and not photo_url:
                photo_url = favicon["href"]
                if not photo_url.startswith("https://") or not photo_url.startswith("http://"):
                    photo_url = "https://" + domain + photo_url
            else:
                photo_url = None

            if not domain.startswith("https://") and not domain.startswith("http://"):
                author_url = "https://" + domain

            if page_title[:10] == p_tag[:10]:
                page_title = None

            h_entry = {"p-name": page_title, "post_body": p_tag, "author_image": photo_url, "author_url": domain, "author_name": domain}

            return h_entry, site_supports_webmention
        except:
            pass

    return h_entry, site_supports_webmention