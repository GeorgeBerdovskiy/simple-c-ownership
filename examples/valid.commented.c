
int main() {
    char * a = (char *) malloc(50 * sizeof(char)); // We know 'a' must be owning
    char * b = a;                                  // It's unclear whether we should transfer ownership from 'a' to 'b'
    free(b);                                       // Since 'free' must be called on owning pointers, we must transfer
                                                   // ownership from 'a' to 'b' on the previous line
}