import requests
import logging
import http.client as http_client
import ast

def custom_print(*args, **kwargs):
    message = ' '.join([str(arg) for arg in args])
    if 'api.openai.com' in message:
        requests_log.debug(message)

http_client.print = custom_print
http_client.HTTPConnection.debuglevel = 1

# Configure basicConfig to write logs to a file
log_filename = 'requests.log'
logging.basicConfig(filename=log_filename, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(log_filename, mode='a')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Configure the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Configure the 'requests.packages.urllib3' logger
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.addHandler(file_handler)
requests_log.propagate = False

def print_recent_requests(n = 1, file = "requests.log"):

    with open(file, "r") as f:
        log = f.read()

    prompt_pattern = re.compile(r'data=\'({.*?})\'', re.DOTALL)
    message_pattern = re.compile(r'"messages": (\[.*?\}\])', re.DOTALL)
    prompt_text_pattern = re.compile(r'"prompt": "(.*?)(?<!\\\\)"', re.DOTALL)

    log_lines = log.splitlines()

    extracted_prompts = []

    for line in log_lines:
        prompt_match = prompt_pattern.search(line)

        if prompt_match:
            json_string = prompt_match.group(1)
            messages_match = message_pattern.search(json_string)
            if messages_match:
                messages_json_string = messages_match.group(1).replace('\\\\', '\\').replace('\\"', '"')
                #messages = json.loads(messages_json_string)
                #user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
                extracted_prompts.append("---Chat prompt:--- " + messages_json_string)
            else:
                prompt_text_match = prompt_text_pattern.search(json_string)
                if prompt_text_match:
                    prompt_text = prompt_text_match.group(1).replace('\\"', '"')
                    extracted_prompts.append("---Text prompt:--- " + prompt_text)
                    
    for i, prompt in enumerate(reversed(extracted_prompts)):
        if i < n:
            prompt = re.sub(r"\\+n", r"\n", prompt)
            print(f"\n{'-'*100}\nOrder: {i}\n{'-'*100}\n")
            print(prompt)
        else:
            break
            
def clear_log_file(file="requests.log"):
    with open(file, "w") as f:
        pass
    
    
def extract_prompts(log):
    prompt_pattern = re.compile(r'data=\'({.*?})\'', re.DOTALL)
    message_pattern = re.compile(r'"messages": (\[.*?\])', re.DOTALL)
    prompt_text_pattern = re.compile(r'"prompt": "(.*?)(?<!\\\\)"', re.DOTALL)

    log_lines = log.splitlines()

    extracted_prompts = []

    for line in log_lines:
        prompt_match = prompt_pattern.search(line)

        if prompt_match:
            json_string = prompt_match.group(1)
            messages_match = message_pattern.search(json_string)
            if messages_match:
                messages_json_string = messages_match.group(1).replace('\\"', '"')
                messages = json.loads(messages_json_string)
                user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
                extracted_prompts.extend(user_messages)
            else:
                prompt_text_match = prompt_text_pattern.search(json_string)
                if prompt_text_match:
                    prompt_text = prompt_text_match.group(1).replace('\\"', '"')
                    extracted_prompts.append(prompt_text)

    return extracted_prompts
