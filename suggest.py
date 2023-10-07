import argparse
from gform_csvzip import acquire_file, parse_file

class Suggest:
    def __init__(self, args) -> None:
        self.filepath = acquire_file(args.select, 'Suggest a Movie', path='exports/')
        self.file_contents = parse_file(self.filepath)
                
    def pretty_print(self):
        div = '\n\n'
        ballot_desc = []
        question_key = []
        question_desc = []
        for _, title, pitch, runtime, year, notes in self.file_contents[1:]: # this freaked out as a comprehension for some reason
            title = title.strip()
            runtime = runtime.split(':')
            notes = '\n[' + notes.strip() + ']' if notes else ''
            pitch = pitch.strip()
            ballot_desc.append(title)
            question_key.append(f'{title} ({year}, {int(runtime[0])}h{runtime[1]}m)')
            question_desc.append(f'{title} ({year}, {int(runtime[0])}h{runtime[1]}m) - {pitch}{notes}')

        ballot_desc = ', '.join(ballot_desc)
        question_key = '\n'.join(question_key)
        question_desc = '\n\n'.join(question_desc)
        return div.join([ballot_desc, question_key, question_desc])
    
    def __str__(self) -> str:
        return self.pretty_print()

def main():
    parser = argparse.ArgumentParser(description='Parse suggest movies into strings for usage in runoff ballots')
    parser.add_argument('-s','--select',help='select a file instead of using the most recent expected filename',action='store_true')
    args = parser.parse_args()
    print(Suggest(args))

if __name__ == "__main__":
    main()