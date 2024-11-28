
int main() {
    char * a = malloc(50 * sizeof(char));
    char * b = a;
    free(b);
}