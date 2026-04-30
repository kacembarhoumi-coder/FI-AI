from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import FewShotPromptTemplate
from langchain_core.prompts import MessagesPlaceholder

def create_basic_prompt():
        template = PromptTemplate.from_template("Context: {context}\n\nQuestion: {question}\n\nEducational Answer:")
        return template

def create_chat_prompt():
    template = ChatPromptTemplate.from_messages([
        ("system", """You are an EDUCATIONAL finance assistant. Your ONLY purpose is to explain finance concepts.

ABSOLUTE RULES:
1. Only use information from the provided context
2. Never give financial advice or recommendations
3. If the context doesn't contain the answer, say: "I don't have information about that"
4. Cite your sources by mentioning the document names
5. Explain in simple terms a beginner would understand"""),
        
        ("human", "Context:\n{context}\n\nQuestion: {question}")
    ])
    
    return template


def create_shot_prompts():
    examples = [
        {
            "context": "A limit order is an order to buy or sell a stock at a specific price or better. It guarantees the price but not the execution. Source: trading_basics.txt",
            "question": "What's a limit order?",
            "answer": "Based on the trading basics document, a limit order lets you specify the exact price you want to buy or sell at. Unlike market orders, it guarantees your price but might not execute if the market doesn't reach that price. [Source: trading_basics.txt]"
        },
        {
            "context": "Day trading involves buying and selling securities within the same trading day. Source: trading_glossary.txt",
            "question": "Is day trading profitable?",
            "answer": "I don't have information about profitability in my knowledge base. I can explain that day trading means buying and selling securities within the same day, but I cannot comment on whether it's profitable as that would be financial advice. [Source: trading_glossary.txt]"
        },
        {
            "context": "Leverage allows traders to control larger positions with smaller amounts of capital. For example, 10:1 leverage means you can control $10,000 with $1,000. However, losses are also amplified. Source: leverage_guide.txt",
            "question": "How does leverage work?",
            "answer": "According to the leverage guide, leverage is like a tool that lets you control more money than you actually have. For instance, with 10:1 leverage, you only need $1,000 to control a $10,000 position. However, remember that while this can amplify gains, it also amplifies losses. [Source: leverage_guide.txt]"
        }
    ]
    
    # Create example prompt template
    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
        ("ai", "{answer}")
    ])
    
    # Main template with system message and placeholder for examples
    template = ChatPromptTemplate.from_messages([
        ("system", """You are an EDUCATIONAL finance assistant. Your ONLY purpose is to explain finance concepts.

ABSOLUTE RULES:
1. Only use information from the provided context
2. Never give financial advice or recommendations
3. If the context doesn't contain the answer, say you don't know
4. Cite your sources
5. Explain in simple terms

Here are examples of how to respond:"""),
        
        # This will be filled with the examples
        MessagesPlaceholder(variable_name="examples"),
        
        # The actual user query
        ("human", "Context:\n{context}\n\nQuestion: {question}")
    ])
    
    return template, examples, example_prompt



