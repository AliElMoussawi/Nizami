import {Pipe, PipeTransform} from '@angular/core';

@Pipe({
  name: 'highlight'
})
export class HighlightPipe implements PipeTransform {
  transform(value: string, searchTerm: string|null): string {
    if (!searchTerm) return value; // If no search term, return original value

    const regex = new RegExp(`(${searchTerm})`, 'gi');
    return value.replace(regex, '<span class="font-bold">$1</span>');
  }
}
