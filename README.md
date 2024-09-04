# Pycon Estonia RAG workshop

## How to run the program

```bash
export OPENAI_API_KEY="abc"

poetry install

streamlit run estonia_workshop/app.py
```

## JSON Schema example

### Input text
```
In the heart of a bustling city lives Alex, a 29-year-old software developer with a passion for more than just coding. Outside the confines of his day job, Alex is a man of varied interests and hobbies that span both the intellectual and the adventurous.
On weekends, you can find Alex immersed in the world of photography, capturing the urban landscape's hidden gems with his keen eye for detail. He finds joy in the quiet moments of dawn, where the soft light breathes life into the ordinary, making his photography not just a hobby but a pursuit of beauty in the mundane.
But Alex's interests do not stop at visual arts. He is also an avid reader, with a particular fondness for science fiction and fantasy. His bookshelves are a testament to his love for worlds beyond, filled with titles ranging from classic Asimov to the imaginative realms of Neil Gaiman. Reading, for him, is not just an escape but a way to explore ideas and philosophies, challenging his perceptions and fueling his creativity.
When not behind a lens or lost in a book, Alex embraces the thrill of rock climbing. This hobby, discovered later in life, has taught him the value of persistence and the joy of overcoming fears. Each ascent is a battle against his limits, and with every peak conquered, he finds not just exhilaration but a profound sense of accomplishment.
Music also plays a significant role in Alex's life. He enjoys playing the guitar, a skill he picked up during his college days. Music is his outlet for expression, a way to unwind after a long day's work, and to connect with friends during impromptu jam sessions.
Through his diverse hobbies, Alex has crafted a life that balances the demands of his career with his quest for personal fulfillment. His story is a reminder that within each of us lies a multitude of interests waiting to be explored, and that age is but a number in the pursuit of passion.
```

### JSON Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Generated schema for Root",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Full name of the person"
    },
    "age": {
      "type": "number",
      "description": "Age of the person"
    }
  },
  "required": [
    "name",
    "age"
  ]
}
```
