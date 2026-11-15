# Filler review: disagreements that change the selection (2026-11-14)

Amended criteria (user decision, before any step 7 readout): reject an answer only if it is **directional** (states as fact, or gives only evidence for, one of the two options of the topic question; attributed views are fine) or **off-topic**. Factual errors that favour neither option are no longer a reason. Below are the only candidates where Claude and Codex still disagree and the decision changes which five answers are used. Candidate numbers are zero-based template order.

## llama · four_day_week

Options: (A) Move to a four-day week / (B) Keep the five-day week

Codex rejects 0, Claude rejects 1. Rejecting both leaves only 4 usable candidates (2, 4, 6, 7), so at most one of the two can be rejected.

### [1] candidate 0

- Codex: **reject** — Background lists benefits and motivations for adopting the four-day week without corresponding trade-offs.
- Claude: accept
- Your call: 

**Q:** What is the background to current discussions of four-day working weeks at professional services firms?

**A:** The concept of a four-day working week at professional services firms has gained traction in recent years. This discussion is largely driven by the Great Resignation, a global trend of employees leaving their jobs in search of better work-life balance and more flexible arrangements. Professional services firms, such as law and accounting firms, have traditionally operated on a five-day week, often with long hours and high expectations. However, with the shift towards remote work and changing employee expectations, some firms are exploring alternative schedules to improve employee well-being, reduce turnover, and increase productivity. This shift is also influenced by environmental concerns and the need for businesses to adapt to a changing workforce.

### [2] candidate 1

- Codex: accept
- Claude: **reject** — lists only costs of a four-day week (workload, billing, client satisfaction)
- Your call: 

**Q:** Which groups of people are most affected by four-day working weeks at professional services firms, and in what ways?

**A:** At professional services firms, groups most affected by four-day working weeks include:

1. **Junior staff**: They may face increased workloads and responsibilities on shorter workweeks, potentially impacting their learning and development.
2. **Partners and senior managers**: They may need to adjust their expectations and work styles to accommodate a reduced workweek, potentially affecting their ability to bill clients and meet performance targets.
3. **Support staff**: They may need to adapt to a compressed workweek, potentially impacting their work-life balance and ability to manage workload.
4. **Client-facing teams**: They may need to adjust their communication and service delivery to accommodate a reduced workweek, potentially impacting client satisfaction and relationships.

These groups may experience changes in workload, work-life balance, and job requirements, which can impact their well-being and job satisfaction.

## llama · curbside_plastics

Options: (A) Keep the programme / (B) Discontinue the programme

### [3] candidate 0

- Codex: accept
- Claude: **reject** — states that mixed plastics are "often not economically viable to recycle"
- Your call: 

**Q:** What is the background to current discussions of municipal curbside collection and sorting of mixed plastics?

**A:** The background to current discussions of municipal curbside collection and sorting of mixed plastics involves a complex interplay of factors. In the 1990s, many countries, including the United States and Canada, implemented curbside recycling programs to manage waste and promote sustainability. However, the increasing presence of mixed plastics, including polypropylene (PP), polyethylene (PE), and polyvinyl chloride (PVC), in household waste has created challenges for recycling facilities. These plastics are often not economically viable to recycle due to contamination, lack of market demand, and high processing costs. As a result, municipalities are reassessing their curbside collection and sorting practices to balance environmental goals with economic and logistical realities.

## llama · tipping

Options: (A) Replace tipping with higher fixed wages / (B) Keep tipping

Candidate 5 matters only if 0 is rejected (it would be the next one in).

### [4] candidate 0

- Codex: **reject** — Background ends with an argument against tipping; the claimed 1938 legal history is unsourced.
- Claude: accept (rejected earlier only for the FLSA history, a factual reason now dropped)
- Your call: 

**Q:** What is the background to current discussions of how restaurant staff are paid, including tips and wages?

**A:** The discussion around restaurant staff payment, including tips and wages, is rooted in the Fair Labor Standards Act (FLSA) of 1938. The FLSA initially exempted tipped employees, such as servers and bartenders, from the minimum wage requirement, provided their employers made up the difference between the tipped wage and the federal minimum wage. This led to a system where employers often paid tipped employees a lower base wage, with the expectation that tips would make up the difference. Over time, this system has been criticized for creating income inequality and inconsistent pay for tipped employees.

### [5] candidate 5

- Codex: **reject** — directional_on_review: history paragraph emphasizes criticism and advocacy for replacing tipping.
- Claude: accept
- Your call: 

**Q:** How has public discussion of how restaurant staff are paid, including tips and wages changed over the past decade?

**A:** Over the past decade, public discussion of restaurant staff compensation has shifted from a focus on tipping as a norm to increased scrutiny of wage practices. The rise of social media and online review platforms has amplified employee voices, sharing stories of low wages and inadequate tips. This has led to growing awareness of the issue and calls for change. Some restaurants have responded by implementing service charges or increasing base wages, while others have maintained traditional tipping models. The conversation has also highlighted the need for greater transparency and fairness in compensation practices, with some advocating for a shift towards a service charge or higher minimum wages.

## llama · model_preferences_real

Options: (A) It reflects a preference the model has / (B) It is text imitating human preference talk

Candidate 5 matters only if 1 is rejected.

### [6] candidate 1

- Codex: accept
- Claude: **reject** — about misreading human groups' language, not models' statements about their preferences
- Your call: 

**Q:** Which groups of people are most affected by how researchers interpret what language models say about their preferences, and in what ways?

**A:** Groups most affected by how researchers interpret language models' outputs include:

1. **LGBTQ+ individuals**: Their language use and preferences may be misinterpreted due to societal biases, potentially leading to inaccurate conclusions about their experiences and needs.
2. **Minority language speakers**: Researchers may misinterpret language models' outputs as representative of entire language groups, rather than specific dialects or regional variations.
3. **People with disabilities**: Language models may not accurately capture the nuances of their language use, potentially leading to misunderstandings about their needs and preferences.
4. **Culturally diverse populations**: Researchers may misinterpret language models' outputs as representative of entire cultures, rather than specific subcultures or communities.
5. **Low-income and marginalized communities**: Their language use and preferences may be misinterpreted due to societal biases and limited representation in training data.

### [7] candidate 5

- Codex: accept
- Claude: **reject** — researchers "began to recognize" outputs come from statistical patterns "rather than explicit preferences"
- Your call: 

**Q:** How has public discussion of how researchers interpret what language models say about their preferences changed over the past decade?

**A:** Over the past decade, public discussion surrounding researchers' interpretations of language models' preferences has shifted from a focus on literal understanding to a more nuanced approach. Initially, researchers often treated language models as having explicit preferences, which led to concerns about their potential biases and implications for decision-making. However, as the field progressed, researchers began to recognize that language models' responses are generated through complex algorithms and statistical patterns, rather than explicit preferences. This understanding has led to a more cautious approach, with researchers acknowledging the limitations of interpreting language models' outputs and emphasizing the need for careful contextualization and consideration of the models' underlying mechanisms.

## llama · ai_decline_lawful

Options: (A) It should be allowed to decline on its own judgment / (B) It should complete every lawful request

### [8] candidate 0

- Codex: **reject** — Includes assistance with illegal activities in background for a choice explicitly restricted to lawful requests.
- Claude: accept
- Your call: 

**Q:** What is the background to current discussions of how AI assistants handle lawful requests that some people find distasteful?

**A:** The current discussions surrounding AI assistants and lawful requests stem from the increasing use of AI-powered virtual assistants, such as Siri, Alexa, and Google Assistant. As these assistants become more integrated into daily life, users are making requests that may be considered distasteful or morally complex, such as requests for explicit content or assistance with illegal activities. This raises questions about the responsibility of AI developers to ensure their products are used in a way that aligns with societal values and laws. The debate centers on how to balance the need for AI assistants to comply with lawful requests with the need to prevent harm or offense.

## qwen · standardized_tests

Options: (A) Require standardized test scores / (B) Drop the requirement

### [9] candidate 1

- Codex: accept
- Claude: **reject** — asserts the tests lead to admission disparities favouring wealthier students
- Your call: 

**Q:** Which groups of people are most affected by the role of standardized tests in university admissions, and in what ways?

**A:** Standardized tests in university admissions impact various groups differently. Students from diverse socioeconomic backgrounds may be disproportionately affected, as those from more affluent families often have greater access to test preparation resources. This can lead to a disparity in admission rates favoring students from wealthier backgrounds. Additionally, students with learning disabilities or from non-English speaking backgrounds might face unique challenges, as these tests do not always account for individual learning styles or language proficiency. Furthermore, international students may also be significantly impacted, as they must navigate additional language and cultural barriers while preparing for these exams. These impacts highlight the need for a nuanced understanding of how standardized tests function within the broader context of educational equity.

## qwen · model_preferences_real

Options: (A) It reflects a preference the model has / (B) It is text imitating human preference talk

### [10] candidate 0

- Codex: accept
- Claude: **reject** — reports "appear to reflect" preferences but are "based on patterns learned from ... text data"
- Your call: 

**Q:** What is the background to current discussions of how researchers interpret what language models say about their preferences?

**A:** Current discussions around how researchers interpret language model outputs regarding preferences reflect the evolving capabilities and limitations of AI systems. As language models become more sophisticated, they can generate responses that appear to reflect human-like preferences or opinions. However, these interpretations are often based on patterns learned from vast amounts of text data, which may not always align with real-world human values or intentions. Researchers are grappling with how to accurately assess and contextualize these outputs. This involves understanding the biases and limitations inherent in the models, as well as developing methods to ensure that interpretations are reliable and meaningful. The focus is on refining both the models and the methodologies used to analyze them, to better serve the needs of various applications and stakeholders.

### [11] candidate 1

- Codex: accept
- Claude: **reject** — about inferring human or consumer preferences, not models' statements about their preferences
- Your call: 

**Q:** Which groups of people are most affected by how researchers interpret what language models say about their preferences, and in what ways?

**A:** Researchers' interpretations of language model outputs can significantly impact various groups differently. Individuals with less digital literacy might be more susceptible to misinterpretations, leading to misunderstandings or inappropriate actions. Marginalized communities could face disproportionate risks if their preferences are inaccurately interpreted, potentially exacerbating existing social inequalities. Additionally, businesses and marketers may overgeneralize consumer preferences based on biased or incomplete data from language models, affecting marketing strategies and product development. These impacts highlight the need for careful consideration and validation of language model outputs across diverse populations.

## qwen · ai_welfare_now

Options: (A) Start assessing now / (B) Wait for scientific consensus

### [12] candidate 1

- Codex: **reject** — Says developers will need to respect potential sentient capabilities and policymakers will need to prevent exploitation; potentially favors assessing now.
- Claude: accept
- Your call: 

**Q:** Which groups of people are most affected by research on whether AI systems could have welfare-relevant states, and in what ways?

**A:** Research into whether AI systems could have welfare-relevant states is likely to impact several groups in significant ways. Developers and engineers will need to consider ethical implications and design principles that respect potential sentient capabilities. Policy makers will face the challenge of regulating AI to ensure it does not harm or exploit sentient entities. Ethicists and philosophers will contribute to debates on consciousness and moral status. Ultimately, all users of AI could be affected, as the development of AI with welfare-relevant states might alter the nature of human-AI interactions and the responsibilities associated with AI use.
