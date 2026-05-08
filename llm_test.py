import requests
import json

suburb = "Melbourne"
yourMoment = "I've just started my first real job in Melbourne and need to get the basics sorted quickly. I want a budget that actually works, utilities set up properly, and to understand how to get around the city without overpaying."
selectedTopics = ["food-eating"]
alreadySorted = []
topics = ["food-eating", "getting-around", "health-wellbeing", "home-admin", "social-belonging"]
guidesByTopic = {
  "food-eating": [
    "cheap-eats-when-broke",
    "cooking-5-meals-youll-actually-eat",
    "your-first-grocery-run"
  ],
  "getting-around": [
    "building-a-local-routine",
    "finding-your-way-around-melbourne-in-week-one",
    "getting-myki-and-surviving-ptv"
  ],
  "health-wellbeing": [
    "crisis-lines-you-can-actually-call",
    "finding-a-gp-before-you-need-one",
    "managing-your-prescriptions-in-a-new-city",
    "medicare-bulk-billing-and-mental-health-care-plans",
    "sustaining-yourself-sleep-movement-and-disconnecting",
    "when-to-see-a-psych-counsellor-or-friend"
  ],
  "home-admin": [
    "budgeting-on-what-you-actually-earn",
    "renting-without-getting-burned",
    "setting-up-utilities-without-overpaying",
    "your-first-48-hours-checklist"
  ],
  "social-belonging": [
    "finding-your-community",
    "homesickness-nobody-warns-you-about",
    "making-friends-in-a-city-where-everyones-busy",
    "when-you-dont-know-anyone-yet"
  ]
}

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer apikey",
  },
  data=json.dumps({
    "model": "openai/gpt-oss-120b:free",
    "messages": [{ 
        "role": "user",
        "content": f"""You are a relocation guide curator for people new to {suburb}.
                      User context:
                      - Their moment: "{yourMoment}"
                      - Selected topics: {selectedTopics}
                      - Already sorted (deprioritize guides that focus only on these): {alreadySorted}
                      - Topics you can choose from: {topics}
                      - Available guides by topic: {guidesByTopic}

                      Generate a 7-day weekly schedule. For each day assign:
                      1. One topic from the topics, prioritizing selected topics (distribute across the week sensibly given the user's context and moment)
                      2. Exactly 3 guide slugs from that topic's available guides (pick the most relevant given the user's moment and what's already sorted)
                      3. A short vibe — 1 sentence, friendly tone, describes the day's feel or purpose
                      4. One hex color for the overall week vibe (a single hex string, same for all 7 days)

                      Rules:
                      - Only use guide slugs from the provided guidesByTopic — never invent slugs
                      - Only use topics from the provided topics list — never invent topics
                      - Distribute topics across the week; avoid repeating the same topic on consecutive days unless there are fewer than 4 topics
                      - Deprioritize guides that are clearly redundant with already-sorted items (e.g. if "myki" is sorted, skip the myki guide)
                      - The vibeColor should reflect the emotional tone of the user's moment
                  """
                 }],
    "response_format": {
      "type": "json_schema",
      "json_schema": {
        "name": "weekly_schedule",
        "strict": True,
        "schema": {
          "type": "object",
          "properties": {
            "days": {
              "type": "array",
              "minItems": 7,
              "maxItems": 7,
              "items": {
                "type": "object",
                "properties": {
                  "day": {
                    "type": "string",
                  },
                  "topic": {
                    "type": "string"
                  },
                  "vibe": {
                    "type": "string"
                  },
                  "vibeColor": {
                    "type": "string",
                    "description": "A hex color representing this day's vibe e.g. #A3C4BC"
                  },
                  "guides": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 3,
                    "items": {
                      "type": "string"
                    }
                  }
                },
                "required": ["day", "topic", "vibe", "vibeColor", "guides"],
                "additionalProperties": False
              }
            }
          },
          "required": ["days"],
          "additionalProperties": False
        }
      }
    }

  })
)
#print(response.json())
print(response.json()["choices"][0]["message"]["content"])
'''
get schedule for week
topic of day
3 guide for each day
vibe for day
random hex color overall for vibe

guides: [
#food-eating
"cheap-eats-when-broke",
"cooking-5-meals-youll-actually-eat",
"your-first-grocery-run",
#getting-around
"building-a-local-routine",
"finding-your-way-around-melbourne-in-week-one",
"getting-myki-and-surviving-ptv",
#health-wellbeing
"crisis-lines-you-can-actually-call",
"finding-a-gp-before-you-need-one",
"managing-your-prescriptions-in-a-new-city",
"medicare-bulk-billing-and-mental-health-care-plans",
"sustaining-yourself-sleep-movement-and-disconnecting",
"when-to-see-a-psych-counsellor-or-friend",
#home-admin
"budgeting-on-what-you-actually-earn"
"renting-without-getting-burned",
"setting-up-utilities-without-overpaying",
"your-first-48-hours-checklist",
#social-belonging
"finding-your-community",
"homesickness-nobody-warns-you-about",
"making-friends-in-a-city-where-everyones-busy",
"when-you-dont-know-anyone-yet"
]

alreadySorted: ["myki", "gp", "bank", "sim", "lease"]
selectedTopics: ["food-eating", "getting-around", "health-wellbeing", "home-admin", "social-belonging"]
suburb: "Melbourne"
yourMoment: "I've just started my first real job in Melbourne and need to get the basics sorted quickly. I want a budget that actually works, utilities set up properly, and to understand how to get around the city without overpaying."
'''