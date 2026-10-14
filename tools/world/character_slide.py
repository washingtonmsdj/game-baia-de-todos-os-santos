"""Seleciona contato lateral real da cápsula; horizontal não gera slide."""
import numpy as np
from slice_geometry import capsule_distances


def lateral_contact(previous, proposed, witness, triangles, radius, height, skin):
    """Retorna índice local/normal, ou None; sem gerar trajetória/navmesh.

    A amostra CCD que bloqueou o movimento delimita os contatos relevantes.
    Não se escolhe uma parede distante só por possuir normal horizontal.
    Empates de distância em arestas são resolvidos pela oposição ao movimento.
    A normal deve apontar para o lado ocupado pela cápsula antes do contato.
    Toda projeção resultante ainda precisa passar pelo CCD original.
    """
    tri = np.asarray(triangles, dtype=float)
    delta = np.asarray(proposed, dtype=float) - previous
    if not len(tri) or np.linalg.norm(delta[:2]) < 1e-10:
        return None
    previous = np.asarray(previous, dtype=float)
    witness = np.asarray(witness, dtype=float)
    threshold = radius - skin
    previous_distance = float(capsule_distances(previous, tri, radius, height).min())
    distances = capsule_distances(witness, tri, radius, height)
    if previous_distance < threshold - 1e-10:
        return None  # Não recuperar uma cápsula já penetrante por normal inventada.
    if distances.min() < threshold and previous_distance > threshold + 1e-10:
        # O CCD pode devolver uma testemunha profundamente dentro da caixa:
        # aproximar a borda do contato antes de escolher a face lateral.
        # Só seleção da normal; o CCD original continua obrigatório para o slide.
        low, high = 0., 1.
        for _ in range(28):
            middle = (low + high) / 2
            sample = previous + (witness - previous) * middle
            if capsule_distances(sample, tri, radius, height).min() < threshold:
                high = middle
            else:
                low = middle
        witness = previous + (witness - previous) * high
        distances = capsule_distances(witness, tri, radius, height)
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    length = np.linalg.norm(normals, axis=1)
    horizontal = np.linalg.norm(normals[:, :2], axis=1)
    minimum = float(distances.min())
    # Contato mais próximo/tie, não qualquer superfície dentro do broadphase.
    candidates = np.flatnonzero((length > 1e-10) & (horizontal >= .9 * length)
                               & (distances <= minimum + 1e-7)
                               & (distances < radius - skin))
    choices = []
    midpoint = np.asarray(previous) + [0, 0, height / 2]
    for index in candidates:
        normal = normals[index].copy()
        normal[2] = 0
        normal /= np.linalg.norm(normal)
        side = float(np.dot(midpoint - tri[index].mean(axis=0), normal))
        if abs(side) < 1e-9:
            continue  # Lado inicial indefinido: não presumir recuperação.
        if side < 0:
            normal = -normal
        opposition = -float(np.dot(delta, normal))
        if opposition > 1e-10:
            choices.append((opposition, int(index), normal))
    if not choices:
        return None
    _, index, normal = max(choices, key=lambda row: (row[0], -row[1]))
    return {'index': index, 'normal': normal, 'distance': float(distances[index]),
            'selection_point': witness}


def project_slide(previous, proposed, normal):
    delta = np.asarray(proposed) - previous
    return np.asarray(previous) + delta - normal * min(float(np.dot(delta, normal)), 0.)
