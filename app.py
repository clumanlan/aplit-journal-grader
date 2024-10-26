import streamlit as st
import json
import re
from haystack.components.generators import OpenAIGenerator

OPENAI_API_KEY = st.secrets['OPENAI_API_KEY']
gpt4_client = OpenAIGenerator(model="gpt-4o")

st.title("Frate Train Journal Response Grader")

prompt = st.text_area("Paste the prompt here:")

input_fields = {
        "Main Claim Only": ["main_claim"],
        "Main Claim and One Evidence": ["main_claim", "evidence_one"],
        "Main Claim and One Evidence and Reasoning": ["main_claim", "evidence_one", "reasoning_one"],
        "Main Claim and Two Evidence and Reasoning": ["main_claim", "evidence_one", "reasoning_one", "evidence_two", "reasoning_two"],
        "Complete Journal": ["main_claim", "evidence_one", "reasoning_one", "evidence_two", "reasoning_two", "conclusion_statement"]
    }

journal_entry_option = st.selectbox(
    "Select what you would like critiqued",
    list(input_fields.keys())
)

journal_sections_submitted = {}

for i in input_fields[journal_entry_option]:
    formatted_title = i.replace("_", " ")
    journal_sections_submitted[i] = st.text_area(f"{formatted_title}", placeholder=f"Enter your {formatted_title} here...")

if st.button("Submit"):

    def main_claim_critique(prompt, main_claim):
            
            main_claim_score_rubric = """
                Score of 4: Shows you thought deeply about the question AND text,
                Answers all parts of the prompt,
                Clear and easy to understand, and
                Concise.

                Score of 3: Too long, too much detail,
                OR
                Vague, lacking specificity,
                OR
                Accurate but poorly phrased.

                Score of 2: Only answers part of the prompt,
                OR
                Is inaccurate due to a misinterpretation.

                Score of 1: Does not address any part of the prompt.
                Does not give an argument (merely facts or summary).
                Does not make sense.
                """
            
            main_claim_prompt = f"""
                As if you are an advanced literature highschool teacher, you provide student this prompt: {prompt}.
                The student, in return, provides this thesis claim in response: {main_claim}.
                Please provide a grade and concise critique in bulleted notes based on this rubric: {main_claim_score_rubric}.
                """
            
            return gpt4_client.run(main_claim_prompt)['replies'][0]


    def evidence_critique(main_claim, evidence):
        
        evidence_score_rubric = """
            Score of 4: You have a direct quote (or a specific paraphrase if the situation is appropriate),
            The direct quote fully supports your claim, and 
            Your direct quote has the context needed to understand it.

            Score of 3: No context, or not enough information is given to make the context clear,
            OR
            Too long, making it difficult to identify which parts are significant.

            Score of 2: Paraphrased when a direct quote would be more appropriate,
            OR
            Tangential to the claim (related to the claim but does not directly prove it).

            Score of 1: Evidence is entirely unrelated to the claim,
            OR
            Evidence is paraphrased poorly, thus too confusing to contribute to the argument.
            """


        evidence_prompt = f"""
            You are an advanced literature highschool teacher,  the student has made this claim: {main_claim}.
            To support this claim the student has provided this evidence: {evidence}.
            Please provide a grade and concise critique in bulleted notes based on this rubric: {evidence_score_rubric}.
            """

        return gpt4_client.run(evidence_prompt)['replies'][0]


    def reasoning_critique(main_claim, evidence, reasoning):
        
        reasoning_score_rubric = """
            Score of 4: Identifies the significant aspects of the evidence,
            provides in-depth insight into the text and deepens readers’ understanding, and
            Explains how the evidence proves the claim.

            Score of 3: Broad analysis of the text, not a specific analysis of the quote, 
            OR 
            Accurate, but surface-level, 
            OR 
            Accurate but not developed.

            Score of 2: Inaccurate, 
            OR 
            Too vague to give insight, 
            OR 
            Accurate but does not relate to the claim.

            Score of 1: Incomprehensible, 
            OR 
            Wholly unrelated to evidence and claim,
            OR 
            Evidence is summarized.
            """

        reasoning_prompt = f"""
            You are an advanced literature highschool teacher, the student has provided this evidence: {evidence}.
            The student's main thesis: {main_claim}. To prove their thesis the student has provided this reasoning: {reasoning}.
            Please provide a grade and concise critique in bulleted notes based on this rubric: {reasoning_score_rubric}.
            """
        
        return gpt4_client.run(reasoning_prompt)['replies'][0]
        

    def synthesis_critique(prompt, main_claim, evidence_one, reasoning_one, evidence_two, reasoning_two, conculsion_statement):
        
        synthesis_score_rubric = """
            Score of 4: Connections are made between all points in the paragraph, 
            arrives at a final conclusion about the text based on synthesis, 
            and shows in-depth insight about the text.

            Score of 3: Connections are present but surface-level, 
            OR conclusion is present but surface-level.

            Score of 2: Synthesis or conclusion is missing, inaccurate, or 
            unrelated to the paragraph, 
            OR too vague.

            Score of 1: All parts are inaccurate, OR arguments are merely restated or summarized.
            """
        
        synthesis_prompt = f"""
            As if you are an advanced literature highschool teacher, you provide student this prompt: {prompt}.
            The student, in return, provides this thesis claim in response: {main_claim} and this evidence:
            {evidence_one} and reasoning: {reasoning_one}.
            Along with this evidence: {evidence_two} and reasoning: {reasoning_two}
            Please provide a grade and concise critique of the {conculsion_statement} based on this rubric: {synthesis_score_rubric}.
            """

        return gpt4_client.run(synthesis_prompt)['replies'][0]
    
    journal_sections_critiques = {}
    main_claim = journal_sections_submitted['main_claim']

    for key, value in journal_sections_submitted.items():
        if key == 'main_claim':
            journal_sections_critiques['main_claim'] = main_claim_critique(prompt, value)
        elif key == 'evidence_one':
            journal_sections_critiques['evidence_one'] = evidence_critique(main_claim, value)
        elif key == 'reasoning_one':
            evidence_one = journal_sections_submitted['evidence_one']
            journal_sections_critiques['reasoning_one'] = reasoning_critique(main_claim, evidence_one, value)
        elif key == 'evidence_two':
            journal_sections_critiques['evidence_two'] = evidence_critique(main_claim, value)
        elif key == 'reasoning_two':
            evidence_two = journal_sections_submitted['evidence_two']
            journal_sections_critiques['reasoning_two'] = reasoning_critique(main_claim, evidence_two, value)
        elif key == 'conclusion_statement':
            evidence_one = journal_sections_submitted['evidence_one']
            reasoning_one = journal_sections_submitted['reasoning_one']
            evidence_two = journal_sections_submitted['evidence_two']
            reasoning_two = journal_sections_submitted['reasoning_two']
            journal_sections_critiques['conclusion_statement'] = synthesis_critique(prompt, main_claim, evidence_one, reasoning_one, evidence_two, reasoning_two, value)

    col1, col2, col3 = st.columns([1, 3, 3]) 

    col1.header("Type")
    col2.header("Student Input")
    col3.header("Critique")

    for key, value in journal_sections_submitted.items():

        col1, col2, col3 = st.columns([1, 3, 3]) 
        with col1:
            clean_title = key.replace('_',' ')
            st.write(clean_title) 
        with col2:
            st.write(value)
        with col3:
            st.write(journal_sections_critiques[key]) 