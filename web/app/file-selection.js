export const supportedFileExtensions = [".csv", ".xlsx", ".xls"];

/**
 * Keep only financial-export files Nomi can import.
 *
 * @param {Iterable<File> | ArrayLike<File>} files
 * @returns {File[]}
 */
export function supportedFiles(files) {
  return Array.from(files).filter((file) =>
    supportedFileExtensions.some((extension) =>
      file.name.toLowerCase().endsWith(extension),
    ),
  );
}
