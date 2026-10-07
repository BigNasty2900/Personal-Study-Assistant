import random
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

print("Welcome to your personal Study Assistant!")

notes = []
conversation_history = []
study_history = []

if os.path.exists("conversation_history.json"):
    with open("conversation_history.json", "r") as file:
        conversation_history=json.load(file)

if os.path.exists("notes.json"):
    with open ("notes.json", "r") as file:
        notes=json.load(file)

if os.path.exists("study_history.json"):
    with open("study_history.json", "r") as file:
        study_history=json.load(file)

while True:
    print("\n===== PERSONAL STUDY ASSISTANT =====")
    print("1. Ask a question")
    print("2. Take a quiz")
    print("3. Take notes")
    print("4. View notes")
    print("5. Delete a note")
    print("6. View conversation history")
    print("7. Study Mode")
    print("8. View Study History")
    print("9. Exit")
    print("====================================")


    choice = input("Enter your choice: ")

    if choice=="1":
        question = input("What would you like help with? ").lower().strip()
    
        response = client.responses.create(
            model= "gpt-6-luna",
            input=question
        )

        conversation_history.append((question, response.output_text))

        with open("conversation_history.json", "w") as file:
            json.dump(conversation_history, file)
        
        print(response.output_text)

    elif choice=="2":
            print("\nQuiz mode!")

            questions = [
                ("What type of data is 'Hello'?", "string", "Hello is text, so it is a string."),
                ("What is 25?", "integer", "25 is a whole number, so it is an integer."),
                ("What keyword is used to create a loop that continues while a condition is true?", "while", "The while keyword repeats code as long as a condition is true."),
                ("What function is used to get information from the user?", "input", "The input function allows the program to receive information from the user."),
                ("What function displays information on the screen?", "print", "The print function displays information on the screen.")
            ]

            easy_questions = questions.copy()
            
            medium_questions=[
                ("What does a function allow you to do?", "reuse code", "functions let you reuse code instead of writing the same code repeatedly."),
                ("What data structure uses key-value pairs?", "dictionary", "a dictionary stores information using keys and their corresponding values."),
                ("What keyword is used to make decisions in Python?", "if", "The if keyword lets a program make a decision based on a condition."),
            ]

            hard_questions=[
                ("What data type is used to store True or False?", "boolean", "A boolean can only have two values: True or False."),
                ("What keyword is used to define a function in Python?", "def", "The def keyword is used to create a function."),
                ("What method adds an item to the end of a list?", "append", "The append methods adds a new item to the end of a list."),
            ]
            difficulty = input("Choose a difficulty (easy, medium, hard): ").lower().strip()
            
            score=0
            if difficulty=="easy":
                quiz_questions=easy_questions.copy()
            elif difficulty=="medium":
                quiz_questions=medium_questions.copy()
            elif difficulty=="hard":
                quiz_questions=hard_questions.copy()
            else:
                print("Invalid difficulty. Please choose easy, medium, or hard.")
                continue

            random.shuffle(quiz_questions)

            for number, (question, answer, explanation) in enumerate(quiz_questions, start=1):
                print("Question", number, "of", len(quiz_questions))
                user_answer = input(question + " ").lower()
                
                if user_answer == answer:
                    print("Correct!")
                    score = score + 1
                else:
                    print("Incorrect. The correct answer is", answer)
                    print("Why:", explanation)

            print("Your score is:", score, "/ ", len(quiz_questions))

    elif choice=="3":
        note = input("What would like to save?")
        notes.append(note)

        with open("notes.json", "w") as file:
            json.dump(notes, file)

        print("Note saved!")

    elif choice == "4":
        if len(notes)==0:
            print("You do not have any notes yet.")
        else:
            print("\nYour notes:")
            for note in notes:
                print("-",note)

    elif choice == "5":
        if len(notes)==0:
            print("You do not have any notes to delete.")
        else:
            print("\nYour notes:")
            for number, note in enumerate(notes, start=1):
                print(number, "_", note)
        try:
            note_number = int(input("What would you like to delete? "))
            
            if 1 <= note_number <= len(notes):
                    notes.pop(note_number - 1)
                    print("Note deleted!")
            else:
                print("Invalid note number.")
        except ValueError:
                print("Please enter a valid note number.")

    elif choice =="6":
        if len (conversation_history)== 0:
            print("You don't have any conversation history yet.")
        else:
            print("\nConversation history:")
            for question, answer in conversation_history:
                print("\nYou:", question)
                print("AI:", answer)

    elif choice=="7":
        while True:
            topic=input("What would you like to study today?")

            print("\nCreating your study lesson...\n")

            response=client.responses.create(
                model= "gpt-6-luna",
                input=f"Teach me about {topic}. Give me a short explanation, an important point to remember, and exactly 3 practice questions. Number the questions 1, 2, and 3. After the questions, do not give the answers."
            )
            
            print("\n" + response.output_text)
            print("\n" + "=" * 50)

            score=0

            print("\nLet's practice what you just learned!")

            for number in range(1, 4):
                question_response = client.responses.create(
                    model = "gpt-6-luna",
                    input=f"Ask me one practice question about {topic}. This is practice question {number} of 3. Give ONLY the question, no answer."
                )
                
                question = question_response.output_text

                print(f"\nQuestion {number}: {question}")

                user_answer = input("Your answer: ")

                check_response = client.responses.create(
                    model="gpt-6-luna",
                    input=f"Topic: {topic}\nQuestion: {question}\nStudent's answer: {user_answer}\n\nCheck the student's answer. Your response MUST start with exactly either CORRECT or INCORRECT. Then briefly explain why."
                )

                print("\n" + check_response.output_text)
                
                if check_response.output_text.strip().lower().startswith("correct"):
                    score +=1

            print(f"\nYour final score: {score}/3")

            study_history.append({
                "topic": topic,
                "score": score
            })

            if score==3:
                print("Excellent! You really understand this topic! 🎉")
            elif score==2:
                print(" Good job! You understand most of it, but review a little more.")
            elif score==1:
                print("Keep practicing! Reviewing this topic again would help.")
            else:
                print("Let's review this topic again and keep practicing. 💪")
        
            try_again=input("\nWould you like to try this topic again? (yes/no): ")

            if try_again.lower()=="yes":
                print("\nLet's try again!")
            else:
                print("\nReturning to the main menu...")
                break

    elif choice=="8":
        print("\n===== STUDY HISTORY =====")

        if len(study_history)==0:
            print("No study history sessions yet.")
        else:
            for session in study_history:
                print(f"Topic: {session['topic']} | Score: {session['score']}/3")

        print("=" * 30)

    elif choice=="9":
        print("Thanks for using your Personal Study Assistant!")
        break
   
    else:
        print("Invalid choice. Please enter a number from 1 to 9.")