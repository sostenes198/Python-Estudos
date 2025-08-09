import yfinance as yf
import openai
import json
import dotenv

dotenv.load_dotenv()

client = openai.Client()


def return_price(ticker, period="1mo"):
    if not ticker.endswith(".SA"):
        ticker = ticker + ".SA"

    ticker_obj = yf.Ticker(f"{ticker}")
    hist = ticker_obj.history(period=period)["Close"]
    hist.index = hist.index.strftime("%Y-%m-%d")
    hist = round(hist, 2)

    if len(hist) > 30:
        slice_size = int(len(hist) / 30)
        hist = hist.iloc[::-slice_size][::-1]

    return hist.to_json()


tools = [
    {
        "type": "function",
        "function": {
            "name": "return_price",
            "description": "Return ticket price",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Ticker B3SA3 BBDC4, etc..."
                    },
                    "period": {
                        "type": "string",
                        "description": "Return period from history ticket. "
                                       "'1mo' means one month, '1d' means one day, '1y' means one year, "
                                       "'ytd' means year to date (from beginning of the year to today).",
                        "enum": ["1d", "5d", "1mo", "6mo", "1y", "5y", "10y", "ytd", "max"]
                    }
                }
            }
        }
    }
]

available_function = {"return_price": return_price}

if __name__ == '__main__':
    messages = [
        {"role": "user", "content": "Qual é a cotação da gerdau nos últimos 10 dias?"}
    ]

    answer = client.chat.completions.create(
        messages=messages,
        model='gpt-3.5-turbo-0125',
        tools=tools,
        tool_choice="auto"
    )

    tool_calls = answer.choices[0].message.tool_calls

    print(tool_calls)

    if tool_calls:
        messages.append(answer.choices[0].message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_function[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_return = function_to_call(**function_args)
            messages.append(
                {"tool_call_id": tool_call.id, "role": "tool", "name": function_name, "content": function_return}
            )

            second_answer = client.chat.completions.create(
                messages=messages,
                model='gpt-3.5-turbo-0125',

            )

            messages.append(second_answer.choices[0].message)
            print(second_answer.choices[0].message.content)
