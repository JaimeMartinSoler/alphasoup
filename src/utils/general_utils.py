
def split_list_in_chunks(lst, chunk_size):
    list_of_chunks = []
    for i in range(0, len(lst), chunk_size):
        list_of_chunks.append(lst[i:i + chunk_size])
    return list_of_chunks


def split_list_in_chunks_equals(lst, chunk_num):
    list_of_chunks = []
    chunk_size_int = int(len(lst) / chunk_num)  # 2
    chunk_size_mod = len(lst) % chunk_num  # 2
    chunk_size_list = [chunk_size_int + 1 if i < chunk_size_mod else chunk_size_int for i in range(chunk_num)]
    chunk_idx = 0
    for chunk_size in chunk_size_list:
        list_of_chunks.append(lst[chunk_idx: chunk_idx+chunk_size])
        chunk_idx += chunk_size
    return list_of_chunks
