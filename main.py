from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, InlineQueryHandler, ChosenInlineResultHandler
import pandas as pd
from txtai import Embeddings

from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

def get_data(filename: str) -> pd.DataFrame:
    columns = ['word', 'type', 'descriptions']
    df = pd.read_csv(filename, names=columns, header=None)
    df = df.fillna('')
    df['complete_description'] = df['type'] + ' ' + df['descriptions']

    return df

def train_embeddings(unique_words: list) -> Embeddings:
    embeddings = Embeddings({
        "path": "sentence-transformers/all-MiniLM-L6-v2",
    })
    embeddings.index(unique_words)

    return embeddings


def similar_words(query: str) -> list:
    results = embedded.search(query, 5)
    words = [unique_words[index] for index,score in results]
    return words

async def inline_search(update, context):
    user_name = update.inline_query.from_user.username
    query = update.inline_query.query
    if not query:
        return

    print(f'{user_name} searched for {query}')

    words = similar_words(query)
    
    results = []
    for i, word in enumerate(words):
        results.append(
            InlineQueryResultArticle(
                id=word,
                title=word,
                input_message_content=InputTextMessageContent(word_description(word))
            )
        )

    await context.bot.answer_inline_query(update.inline_query.id, results)

def word_description(word):
    message = f"**{word}**\n"
    descriptions = df.loc[df['word'] == word]['complete_description'].tolist()
    for i, description in enumerate(descriptions):
        message += f'{i+1}. {description}\n'
    return message


df = get_data('src/dictionary.csv')
unique_words = df['word'].unique()
embedded = train_embeddings(unique_words)

def main() -> None: 
    application = Application.builder().token(TELEGRAM_TOKEN).build()


    # inline search
    application.add_handler(InlineQueryHandler(inline_search))
    application.run_polling()

if __name__ == "__main__":
    print('Started')
    main()

