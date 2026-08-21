from r2_management.r2_management import R2Management
import os

from dotenv import load_dotenv
from colorama import Fore, init    

OPERATION_MAPPING = {
    1: "upload",
    2: "upload_multiple",
    3: "download",
    4: "list",
    5: "delete",
    6: "exit"
}

# enum for UI state
SELECTING_OPERATION = 0
INPUTTING_ARGUMENT = 1
COMFIRMING_OPERATION = 2
OPERATE = 3

# enum for operation
OPERATION_UPLOAD = 1
OPERATION_UPLOAD_MULTIPLE = 2
OPERATION_DOWNLOAD = 3
OPERATION_LIST = 4
OPERATION_DELETE = 5
OPERATION_EXIT = 6

NUM_OF_OPERATIONS = max(OPERATION_UPLOAD,
    OPERATION_UPLOAD_MULTIPLE,
    OPERATION_DOWNLOAD,
    OPERATION_LIST,
    OPERATION_DELETE,
    OPERATION_EXIT
    )

def create_default_state():
    return {
        "step": SELECTING_OPERATION,
        "operation": None,
        "argument_number": None,
        "user_argument": [],
        "current_list": []
    }

def ui_init():
    init()
    
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def run_operation(r2, operation, args):
    if operation == OPERATION_UPLOAD:
        obj_link = r2.upload(args[0],args[1])
        return f"The image is uploaded to {obj_link}"
    if operation == OPERATION_UPLOAD_MULTIPLE:
        processed_arg0 = args[0].split(" ")
        obj_links = r2.upload_multiple(processed_arg0,args[1])
        return obj_links
    if operation == OPERATION_DOWNLOAD:
        image_path = r2.download(args[0],args[1])
        return f"The image is downloaded to {image_path}"
    if operation == OPERATION_LIST:
        return r2.list()
    if operation == OPERATION_DELETE:
        r2.delete(args[0])
        return f"{args[0]} is deleted"
    

def get_argument_name(operation):
    args_name = []
    if operation == OPERATION_UPLOAD:
        args_name = ["file_path", "object_name"]
    elif operation == OPERATION_UPLOAD_MULTIPLE:
        args_name = ["file_paths(split with space)", "object_dir"]
    elif operation == OPERATION_DOWNLOAD:
        args_name = ["object_name", "file_path"]
    elif operation == OPERATION_DELETE:
        args_name = ["object_name"]
    return args_name

def render_ui(r2, state):
    clear_screen()
    step = state["step"]
    operation = state["operation"]
    argument_number = state["argument_number"]
    user_argument = state["user_argument"]

    if step >= SELECTING_OPERATION:
        # determine display color
        colors = []
        for i in range(1, NUM_OF_OPERATIONS+1, 1):
            if(operation and operation == i):
                colors.append(Fore.GREEN)
            else:
                colors.append(Fore.YELLOW)

        # output
        print(Fore.WHITE + "Select an operation:")
        print(colors[0] + "1. Upload file")
        print(colors[1] + "2. Upload multiple files")
        print(colors[2] + "3. Download file")
        print(colors[3] + "4. List file")
        print(colors[4] + "5. Delete file")
        print(colors[5] + "6. Exit")
        print("")

    # hint display
    if(step == INPUTTING_ARGUMENT and operation == OPERATION_DELETE):
        print("current list:")
        print(run_operation(r2, OPERATION_LIST, []))
        print("")

    if step >= INPUTTING_ARGUMENT and operation in [OPERATION_UPLOAD, OPERATION_UPLOAD_MULTIPLE, OPERATION_DOWNLOAD, OPERATION_DELETE]:
        # decide the argument names on display
        args_name = get_argument_name(operation)

        colors = []
        # decide the color
        for i in range(len(args_name)):
            if i == argument_number and step == INPUTTING_ARGUMENT:
                colors.append(Fore.GREEN)
            else:
                colors.append(Fore.YELLOW)

        # output
        print(Fore.WHITE + "required arguments:")
        for i in range(len(args_name)):
            print(colors[i] + args_name[i])
        print("")

    if step == COMFIRMING_OPERATION and operation in [OPERATION_DELETE]:
        print(Fore.WHITE + f"Are you sure to operate: {OPERATION_MAPPING[operation]}({", ".join(user_argument)})")


def application(r2):
    ui_init()
    state = create_default_state()
    state["current_list"] = run_operation(r2, OPERATION_LIST, [])
    while True:
        next_state = state
        step = state["step"]
        operation = state["operation"]
        argument_number = state["argument_number"]
        user_argument = state["user_argument"]

        if(operation == OPERATION_EXIT):
            break

        render_ui(r2, state)

        if step == SELECTING_OPERATION:
            print("")
            selected_operation = input(Fore.WHITE + "Please select the operation: ")
            if(selected_operation not in [f"{OPERATION_UPLOAD}",f"{OPERATION_UPLOAD_MULTIPLE}",f"{OPERATION_DOWNLOAD}",f"{OPERATION_LIST}",f"{OPERATION_DELETE}",f"{OPERATION_EXIT}"]):
                raise ValueError("Invalid input")
            selected_operation = int(selected_operation)
            selected_operation_arguments = get_argument_name(selected_operation)
            if len(selected_operation_arguments) >= 1:
                next_state["step"] = INPUTTING_ARGUMENT
                next_state["argument_number"] = 0
            else:
                next_state["step"] = OPERATE
            next_state["operation"] = selected_operation
        if step == INPUTTING_ARGUMENT:
            print("")
            arg = input(Fore.WHITE + f"please input the {get_argument_name(operation)[argument_number]}: ")
            next_state["user_argument"].append(arg)
            has_next_arg = argument_number + 1 < len(get_argument_name(operation))
            if(has_next_arg):
                next_state["argument_number"] += 1
            else:
                if operation in [OPERATION_DELETE]:
                    next_state["step"] = COMFIRMING_OPERATION
                else:
                    next_state["step"] = OPERATE
        if step == COMFIRMING_OPERATION:
            print("")
            arg = input(Fore.WHITE + "y/n: ")
            if arg.lower() == "y":
                next_state["step"] = OPERATE
            else:
                print(Fore.YELLOW + "canceled")
                os.system("pause")
                next_state = create_default_state()
        if step == OPERATE:
            print(Fore.WHITE + f"operating: {OPERATION_MAPPING[operation]}({", ".join(user_argument)})")
            output = run_operation(r2, operation, user_argument)
            print(output)
            os.system("pause")
            next_state = create_default_state()

        state = next_state

def throw_error(error, r2):
    print("\n" + Fore.RED + "Unexpected error: " + str(error) + Fore.WHITE)
    os.system("pause")

    # restart
    start_app(r2)

def start_app(r2):
    try:
        application(r2)
    except Exception as e:
        throw_error(e, r2)
    

if __name__ == "__main__":
    load_dotenv()   
    r2_management = R2Management(
        bucket_name=os.getenv("BUCKET"),
        endpoint_url=os.getenv("ENDPOINT"),
        access_key=os.getenv("ACCESS_KEY"),
        secret_key=os.getenv("SECRET_ACCESS_KEY"),
        public_url=os.getenv("PUBLIC_URL")
    )

    start_app(r2_management)
