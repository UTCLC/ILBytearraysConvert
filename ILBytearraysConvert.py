import os
import re
import sys
from binascii import unhexlify

def il_escape(s):
	replacements = [
		('\\', '\\\\'),
		('"', '\\"'),
		('\b', '\\b'),
		('\n', '\\n'),
		('\r', '\\r'),
		('\t', '\\t'),
	]
	for orig, repl in replacements:
		s = s.replace(orig, repl)
	return s

def process_bytearray(hex_block):
	try:
		no_comment = re.sub(r'//.*', '', hex_block, flags=re.MULTILINE)
		if (no_comment == hex_block):
			return f'bytearray({hex_block})'
		clean_hex = re.sub(r'[^0-9A-Fa-f]', '', no_comment, flags=re.IGNORECASE)
		
		if len(clean_hex) % 2 != 0:
			clean_hex += '0'
		
		byte_data = unhexlify(clean_hex)
		
		decoded = byte_data.decode('utf-16-le', errors='surrogatepass')
		escaped = il_escape(decoded)
		
		final = []
		for c in escaped:
			cp = ord(c)
			if cp < 32 or (0x7F <= cp <= 0x9F) or (0xD800 <= cp <= 0xDFFF):
				final.append(f'\\x{cp:02x}' if cp <= 0xFF else f'\\x{cp:04x}')
			else:
				final.append(c)
		if (f'bytearray({hex_block})' != f'"{ "".join(final) }"'):
			print(f"bytearray({hex_block}) found and replaced with { "".join(final) }")
		return f'"{ "".join(final) }"'
	except Exception as e:
		print(f"Failed: {str(e)}", file=sys.stderr)
		return f'bytearray({hex_block})'

def convert_il_file(input_path):
	pattern = re.compile(
		r'(ldstr\s+)bytearray\s*\(\s*((?:.|\n)*?)\)',
		re.DOTALL | re.IGNORECASE
	)

	with open(input_path, 'r', encoding='utf-8-sig') as f:
		content = f.read()

	new_content = pattern.sub(
		lambda m: f'{m.group(1)}{process_bytearray(m.group(2))}',
		content
	)
	os.makedirs(os.path.dirname(input_path)+"/Repacked/",exist_ok=True)
	with open(os.path.dirname(input_path)+"/Repacked/"+os.path.basename(input_path), 'w', encoding='utf-8') as f:
		f.write(new_content)

file = input("File: ").replace("\\","/")
if (file.endswith("/")):
	file = dir[:-1]
convert_il_file(file)