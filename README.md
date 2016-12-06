# pdb-alexa

Peering DB - Alexa Skill
===============================
A custom Alexa Skill for doing basic read-only queries to [Peering DB](https://peeringdb.com)


Alexa Skill Setup:
------------------

1. Create a new custom skill from the [Amazon Developer Console](https://developer.amazon.com/edw/home.html#/)
2. In the Interaction Model tab, first create 3x new custom slots, and paste in the values from the respective files [here](https://github.com/detobate/pdb-alexa/tree/master/custom_slots)
3. Next, paste in the [Intent Scheme](https://github.com/detobate/pdb-alexa/blob/master/intent-schema.json) which defines the intents, and references the custom slots/types we created above.
4. Lastly, each intent requires at least one Sample Utterance to allow Alexa to work out how to match it.  Paste in the [Sample Utterances](https://github.com/detobate/pdb-alexa/blob/master/sample_utterances)
5. Create a new Lambda service in the [AWS Management Console](https://aws.amazon.com/). This will host the Python script that Alexa will call.
6. Use basic settings, with no VPC. (If you select a VPC, you will lose external Internet connectivity from the Lambda)
7. Upload the code as a zip file.  You will need to include the Python module Requests, and UJSON.  The UJSON Python module is a JSON decoder written in C, so sadly you'll need to compile this probably on an EC2 instance first, to match their architecture.  (I could use another JSON decoder, but attempting to make the whole thing faster) 
8. Increase the timeout value under advanced settings.  Some API calls can take awhile to return.

Usage Examples:
---------------

 * Alexa, ask Peering DB, who has AS *ASN*?
 * Alexa, ask Peering DB, where do *ISP* peer?
 * Alexa, ask Peering DB, who peers at *IX*?
  