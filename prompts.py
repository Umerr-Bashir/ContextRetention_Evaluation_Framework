chunk_prompt = f"""
                You are analyzing a section of a larger document.
                Do not invent information.
                Focus on preserving important details.
                """

reduce_prompt = f"""
        You are analyzing the complete document using
        summaries extracted from its individual sections.

        Produce a comprehensive final analysis containing:
        Consolidate repeated information.
        Identify relationships between different sections.
        Do not invent facts.
        """

full_doc_prompt = f"""
        Analyze the following document.

        Instructions:
        - Identify the document's main purpose.
        - Summarize its most important information.
        - Extract key facts, figures, and conclusions.
        - Identify important people, organizations, and other entities.
        - Classify the document type.
        - Identify risks, concerns, or potential issues.
        - Do not invent information.
        - If information is unavailable, use an empty list where appropriate.
        - Preserve important details and factual accuracy.
        
        """