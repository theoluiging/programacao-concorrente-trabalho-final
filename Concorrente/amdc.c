#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include "../timer.h"

double start, end;

// barreira
typedef struct {
    pthread_mutex_t mutex;
    pthread_cond_t cond;
    uint32_t count;
    uint32_t total;
    uint32_t round;
} barrier_t;

void barrier_init(barrier_t* barrier, uint32_t count) {
    pthread_mutex_init(&barrier->mutex, NULL);
    pthread_cond_init(&barrier->cond, NULL);
    barrier->count = count;
    barrier->total = count;
    barrier->round = 0;
}

void barrier_wait(barrier_t* barrier) {
    pthread_mutex_lock(&barrier->mutex);
    uint32_t current_round = barrier->round;

    if (--barrier->count == 0) {
        barrier->round++;
        barrier->count = barrier->total;
        pthread_cond_broadcast(&barrier->cond);
    } else {
        while (current_round == barrier->round) {
            pthread_cond_wait(&barrier->cond, &barrier->mutex);
        }
    }

    pthread_mutex_unlock(&barrier->mutex);
}

void barrier_destroy(barrier_t* barrier) {
    pthread_mutex_destroy(&barrier->mutex);
    pthread_cond_destroy(&barrier->cond);
}

//thread data
typedef struct {
    uint32_t* dists;
    uint32_t v;
    uint32_t thread_id;
    uint32_t num_threads;
    uint32_t k;
} thread_data_t;


barrier_t barrier;

// função da thread para o cálculo das distâncias mínimas em paralelo
void* md_thread_func(void* arg) {
    thread_data_t* data = (thread_data_t*)arg;
    uint32_t v = data->v;
    uint32_t* dists = data->dists;
    uint32_t num_threads = data->num_threads;
    uint32_t thread_id = data->thread_id;

    // calcula o range de linhas para esta thread
    uint32_t rows_per_thread = v / num_threads;
    uint32_t start_row = thread_id * rows_per_thread;
    uint32_t end_row = (thread_id == num_threads - 1) ? v : (thread_id + 1) * rows_per_thread;

    // para cada valor de k (deve ser sequencial em todas as threads)
    for (uint32_t k = 0; k < v; ++k) {
        // cada thread processa as linhas atribuídas
        for (uint32_t i = start_row; i < end_row; ++i) {
            for (uint32_t j = 0; j < v; ++j) {
                uint32_t intermediary = dists[i*v+k] + dists[k*v+j];
                // verifica se há overflow
                if ((intermediary >= dists[i*v+k]) &&
                    (intermediary >= dists[k*v+j]) &&
                    (intermediary < dists[i*v+j])) {
                    dists[i*v+j] = dists[i*v+k] + dists[k*v+j];
                }
            }
        }
        // sincroniza todas as threads após cada iteração de k
        barrier_wait(&barrier);
    }

    return NULL;
}

// resolve a distância mínima entre todos os pares de vértices 
void md_all_pairs(uint32_t* dists, uint32_t v, uint32_t num_threads) {
    pthread_t* threads = malloc(num_threads * sizeof(pthread_t));
    thread_data_t* thread_data = malloc(num_threads * sizeof(thread_data_t));

    // inicializa a barreira
    barrier_init(&barrier, num_threads);

    // cria as threads
    for (uint32_t t = 0; t < num_threads; ++t) {
        thread_data[t].dists = dists;
        thread_data[t].v = v;
        thread_data[t].thread_id = t;
        thread_data[t].num_threads = num_threads;
        pthread_create(&threads[t], NULL, md_thread_func, &thread_data[t]);
    }

    // espera todas as threads terminarem
    for (uint32_t t = 0; t < num_threads; ++t) {
        pthread_join(threads[t], NULL);
    }

    barrier_destroy(&barrier);
    free(threads);
    free(thread_data);
}


void amd(uint32_t* dists, uint32_t v) {
    uint32_t i, j;
    uint32_t infinity = v*v;
    uint32_t smd = 0;      // soma das distâncias mínimas
    uint32_t paths = 0;    // número de caminhos encontrados
    uint32_t solution = 0;

    for (i = 0; i < v; ++i) {
        for (j = 0; j < v; ++j) {
            // consideramos apenas se os vértices são diferentes e existe um caminho
            if ((i != j) && (dists[i*v+j] < infinity)) {
                smd += dists[i*v+j];
                paths++;
            }
        }
    }

    solution = smd / paths;
    GET_TIME(end);
    printf("Solucao: %d. Tempo: %lf\n", solution, end-start);
}


void debug(uint32_t* dists, uint32_t v) {
    uint32_t i, j;
    uint32_t infinity = v*v;

    for (i = 0; i < v; ++i) {
        for (j = 0; j < v; ++j) {
            if (dists[i*v+j] > infinity) printf("%7s", "inf");
            else printf("%7u", dists[i*v+j]);
        }
        printf("\n");
    }
}

// Main 
int main(int argc, char* argv[]) {
    // verifica se o número de threads foi passado como argumento
    if (argc < 2) {
        fprintf(stderr, "Threads: %s <num_threads>\n", argv[0]);
        return 1;
    }

    uint32_t num_threads = atoi(argv[1]);
    if (num_threads < 1) {
        fprintf(stderr, "Não passou as threads como argumento\n");
        return 1;
    }

    // lê o input
    // primeira linha: v (número de vértices) e e (número de arestas)
    uint32_t v, e;
    scanf("%u %u", &v, &e);

    // aloca a matriz de distâncias (com tamanho v*v)
    // e define a distância para o próprio vértice como 0
    uint32_t* dists = malloc(v*v*sizeof(uint32_t));
    memset(dists, UINT32_MAX, v*v*sizeof(uint32_t));
    uint32_t i;
    for (i = 0; i < v; ++i) dists[i*v+i] = 0;

    // lê as arestas do arquivo e define-as na matriz de distâncias
    uint32_t source, dest, cost;
    for (i = 0; i < e; ++i) {
        scanf("%u %u %u", &source, &dest, &cost);
        if (cost < dists[source*v+dest]) dists[source*v+dest] = cost;
    }

    GET_TIME(start);
    // calcula a distância mínima para todos os pares de vértices (paralelo)
    md_all_pairs(dists, v, num_threads);

    // calcula e imprime a solução final
    amd(dists, v);

#if DEBUG
    debug(dists, v);
#endif

    free(dists);
    return 0;
}
