import streamlit as st
import json
import re
from haystack.components.generators import OpenAIGenerator

OPENAI_API_KEY = st.secrets['OPENAI_API_KEY']
gpt4_client = OpenAIGenerator(model="gpt-4o")

st.title("Frate Train Journal Response Grader")

prompt = st.text_area("Paste the prompt here:")
main_claim = st.text_area("Main Claim", placeholder="Enter your main claim here...")
evidence_one = st.text_area("Evidence One", placeholder="Enter your first piece of evidence here...")
reasoning_one = st.text_area("Reasoning One", placeholder="Enter reasoning for evidence one here...")
evidence_two = st.text_area("Evidence Two", placeholder="Enter your second piece of evidence here...")
reasoning_two = st.text_area("Reasoning Two", placeholder="Enter reasoning for evidence two here...")
conclusion_statement = st.text_area("Conclusion Statement", placeholder="Enter your conclusion here...")


if st.button("Submit"):

    claim_score_rubric = """
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

    claim_prompt = f"""
        As if you are an advanced literature highschool teacher, you provide student this prompt: {prompt}.
        The student, in return, provides this thesis claim in response: {main_claim}.
        Please provide a grade and concise critique based on this rubric: {claim_score_rubric}.
        """

    claim_response = gpt4_client.run(claim_prompt)['replies'][0]


    evidence_list = [evidence_one, evidence_two]
    reasoning_list = [reasoning_one, reasoning_two]
    evidence_responses = []
    reasoning_responses = []

    for evidence, reasoning in zip(evidence_list, reasoning_list):

        evidence_prompt = f"""
            You are an advanced literature highschool teacher,  the student has made this claim: {main_claim}.
            To support this claim the student has provided this evidence: {evidence}.
            Please provide a grade and concise critique based on this rubric: {evidence_score_rubric}.
            """

        reasoning_two_prompt = f"""
            You are an advanced literature highschool teacher, the student has provided this evidence: {evidence}.
            The student's main thesis: {main_claim}. To prove their thesis the student has provided this reasoning: {reasoning}.
            Please provide a grade and concise critique in bulleted notes based on this rubric: {reasoning_score_rubric}.
            """
        
        evidence_response = gpt4_client.run(evidence_prompt)
        evidence_responses.append(evidence_response['replies'])
        
        reasoning_response = gpt4_client.run(reasoning_two_prompt)
        reasoning_responses.append(reasoning_response['replies'])


    synthesis_prompt = f"""
        As if you are an advanced literature highschool teacher, you provide student this prompt: {prompt}.
        The student, in return, provides this thesis claim in response: {main_claim} and this evidence:
        {evidence_responses[0][0]} and reasoning: {reasoning_responses[0][0]}.
        Along with this evidence: {evidence_responses[1][0]} and reasoning: {reasoning_responses[1][0]}
        Please provide a grade and concise critique of the {conclusion_statement} based on this rubric: {synthesis_score_rubric}.
        """

    synthesis_response = gpt4_client.run(synthesis_prompt)['replies'][0]

    col1, col2, col3 = st.columns([1, 3, 3]) 

    col1.header("Type")
    col2.header("Student Input")
    col3.header("Response")

    with col1:
        st.write('Main Claim') 
    with col2:
        st.write(main_claim)
    with col3:
        st.write(claim_response) 
    
    
    col1, col2, col3 = st.columns([1, 3, 3])  
    with col1:
        st.write('Evidence #1') 
    with col2:
        st.write(evidence_one)
    with col3:
        st.write(evidence_responses[0][0]) 

    col1, col2, col3 = st.columns([1, 3, 3])  
    with col1:
        st.write('Reasoning #1') 
    with col2:
        st.write(reasoning_one)
    with col3:
        st.write(reasoning_responses[0][0]) 
    
    col1, col2, col3 = st.columns([1, 3, 3])  
    with col1:
        st.write('Evidence #2') 
    with col2:
        st.write(evidence_two)
    with col3:
        st.write(evidence_responses[1][0]) 
    
    col1, col2, col3 = st.columns([1, 3, 3])  
    with col1:
        st.write('Reasoning #2') 
    with col2:
        st.write(reasoning_two)
    with col3:
        st.write(reasoning_responses[1][0]) 
      
    col1, col2, col3 = st.columns([1, 3, 3])  
    with col1:
        st.write('Synthesis') 
    with col2:
        st.write(conclusion_statement)
    with col3:
        st.write(synthesis_response) 
    
  
