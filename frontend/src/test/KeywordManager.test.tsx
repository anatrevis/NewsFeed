import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import KeywordManager from '../components/KeywordManager'
import * as api from '../services/api'

// Mock the API module
vi.mock('../services/api', () => ({
  createKeyword: vi.fn(),
  deleteKeyword: vi.fn(),
}))

const mockKeywords: api.Keyword[] = [
  { id: '1', keyword: 'python', created_at: '2024-01-15T10:00:00Z' },
  { id: '2', keyword: 'javascript', created_at: '2024-01-14T10:00:00Z' },
  { id: '3', keyword: 'react', created_at: '2024-01-13T10:00:00Z' },
]

describe('KeywordManager', () => {
  const mockOnKeywordChange = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders the component title and description', () => {
      render(
        <KeywordManager
          keywords={[]}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      expect(screen.getByText('Your Keywords')).toBeInTheDocument()
      expect(screen.getByText('Add keywords to personalize your news feed')).toBeInTheDocument()
    })

    it('renders the input field and add button', () => {
      render(
        <KeywordManager
          keywords={[]}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      expect(screen.getByPlaceholderText('Enter a keyword...')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /add/i })).toBeInTheDocument()
    })

    it('shows loading spinner when loading is true', () => {
      render(
        <KeywordManager
          keywords={[]}
          onKeywordChange={mockOnKeywordChange}
          loading={true}
        />
      )

      // Check for the loading spinner (has animate-spin class)
      const spinner = document.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()
    })

    it('shows empty state message when no keywords', () => {
      render(
        <KeywordManager
          keywords={[]}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      expect(screen.getByText('No keywords yet. Add some to see personalized news!')).toBeInTheDocument()
    })

    it('renders all keywords as pills', () => {
      render(
        <KeywordManager
          keywords={mockKeywords}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      expect(screen.getByText('python')).toBeInTheDocument()
      expect(screen.getByText('javascript')).toBeInTheDocument()
      expect(screen.getByText('react')).toBeInTheDocument()
    })

    it('renders delete button for each keyword', () => {
      render(
        <KeywordManager
          keywords={mockKeywords}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      // Each keyword pill should have a delete button (X icon)
      const deleteButtons = screen.getAllByRole('button').filter(
        btn => btn.querySelector('svg path[d*="M6 18L18 6"]')
      )
      expect(deleteButtons).toHaveLength(3)
    })
  })

  describe('Adding Keywords', () => {
    it('calls createKeyword when form is submitted', async () => {
      const mockCreateKeyword = vi.mocked(api.createKeyword)
      mockCreateKeyword.mockResolvedValueOnce({
        id: '4',
        keyword: 'typescript',
        created_at: '2024-01-16T10:00:00Z',
      })

      render(
        <KeywordManager
          keywords={[]}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      const input = screen.getByPlaceholderText('Enter a keyword...')
      const addButton = screen.getByRole('button', { name: /add/i })

      await userEvent.type(input, 'typescript')
      await userEvent.click(addButton)

      await waitFor(() => {
        expect(mockCreateKeyword).toHaveBeenCalledWith('typescript')
      })
    })

    it('clears input and calls onKeywordChange after successful add', async () => {
      const mockCreateKeyword = vi.mocked(api.createKeyword)
      mockCreateKeyword.mockResolvedValueOnce({
        id: '4',
        keyword: 'typescript',
        created_at: '2024-01-16T10:00:00Z',
      })

      render(
        <KeywordManager
          keywords={[]}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      const input = screen.getByPlaceholderText('Enter a keyword...')

      await userEvent.type(input, 'typescript')
      await userEvent.click(screen.getByRole('button', { name: /add/i }))

      await waitFor(() => {
        expect(mockOnKeywordChange).toHaveBeenCalled()
        expect(input).toHaveValue('')
      })
    })

    it('disables add button when input is empty', () => {
      render(
        <KeywordManager
          keywords={[]}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      const addButton = screen.getByRole('button', { name: /add/i })
      expect(addButton).toBeDisabled()
    })

    it('disables add button when input has only whitespace', async () => {
      render(
        <KeywordManager
          keywords={[]}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      const input = screen.getByPlaceholderText('Enter a keyword...')
      await userEvent.type(input, '   ')

      const addButton = screen.getByRole('button', { name: /add/i })
      expect(addButton).toBeDisabled()
    })

    it('shows error message when createKeyword fails', async () => {
      const mockCreateKeyword = vi.mocked(api.createKeyword)
      mockCreateKeyword.mockRejectedValueOnce(new Error('Keyword already exists'))

      render(
        <KeywordManager
          keywords={[]}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      const input = screen.getByPlaceholderText('Enter a keyword...')

      await userEvent.type(input, 'python')
      await userEvent.click(screen.getByRole('button', { name: /add/i }))

      await waitFor(() => {
        expect(screen.getByText('Keyword already exists')).toBeInTheDocument()
      })
    })

    it('trims whitespace from keyword before submitting', async () => {
      const mockCreateKeyword = vi.mocked(api.createKeyword)
      mockCreateKeyword.mockResolvedValueOnce({
        id: '4',
        keyword: 'golang',
        created_at: '2024-01-16T10:00:00Z',
      })

      render(
        <KeywordManager
          keywords={[]}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      const input = screen.getByPlaceholderText('Enter a keyword...')

      await userEvent.type(input, '  golang  ')
      await userEvent.click(screen.getByRole('button', { name: /add/i }))

      await waitFor(() => {
        expect(mockCreateKeyword).toHaveBeenCalledWith('golang')
      })
    })

    it('shows loading spinner on add button while submitting', async () => {
      const mockCreateKeyword = vi.mocked(api.createKeyword)
      // Create a promise we can control
      let resolvePromise: (value: api.Keyword) => void
      mockCreateKeyword.mockReturnValueOnce(
        new Promise((resolve) => {
          resolvePromise = resolve
        })
      )

      render(
        <KeywordManager
          keywords={[]}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      const input = screen.getByPlaceholderText('Enter a keyword...')

      await userEvent.type(input, 'rust')
      await userEvent.click(screen.getByRole('button', { name: /add/i }))

      // Should show spinner while loading
      await waitFor(() => {
        const addButton = screen.getByRole('button')
        const spinner = addButton.querySelector('.animate-spin')
        expect(spinner).toBeInTheDocument()
      })

      // Resolve and cleanup
      resolvePromise!({ id: '5', keyword: 'rust', created_at: '2024-01-16T10:00:00Z' })
    })
  })

  describe('Deleting Keywords', () => {
    it('calls deleteKeyword when delete button is clicked', async () => {
      const mockDeleteKeyword = vi.mocked(api.deleteKeyword)
      mockDeleteKeyword.mockResolvedValueOnce()

      render(
        <KeywordManager
          keywords={mockKeywords}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      // Find the python keyword pill and its delete button
      const pythonKeyword = screen.getByText('python')
      const deleteButton = pythonKeyword.parentElement?.querySelector('button')

      await userEvent.click(deleteButton!)

      await waitFor(() => {
        expect(mockDeleteKeyword).toHaveBeenCalledWith('python')
      })
    })

    it('calls onKeywordChange after successful delete', async () => {
      const mockDeleteKeyword = vi.mocked(api.deleteKeyword)
      mockDeleteKeyword.mockResolvedValueOnce()

      render(
        <KeywordManager
          keywords={mockKeywords}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      const pythonKeyword = screen.getByText('python')
      const deleteButton = pythonKeyword.parentElement?.querySelector('button')

      await userEvent.click(deleteButton!)

      await waitFor(() => {
        expect(mockOnKeywordChange).toHaveBeenCalled()
      })
    })

    it('shows error message when deleteKeyword fails', async () => {
      const mockDeleteKeyword = vi.mocked(api.deleteKeyword)
      mockDeleteKeyword.mockRejectedValueOnce(new Error('Failed to delete'))

      render(
        <KeywordManager
          keywords={mockKeywords}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      const pythonKeyword = screen.getByText('python')
      const deleteButton = pythonKeyword.parentElement?.querySelector('button')

      await userEvent.click(deleteButton!)

      await waitFor(() => {
        expect(screen.getByText('Failed to delete')).toBeInTheDocument()
      })
    })

    it('shows loading spinner on delete button while deleting', async () => {
      const mockDeleteKeyword = vi.mocked(api.deleteKeyword)
      let resolvePromise: () => void
      mockDeleteKeyword.mockReturnValueOnce(
        new Promise((resolve) => {
          resolvePromise = resolve
        })
      )

      render(
        <KeywordManager
          keywords={mockKeywords}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      const pythonKeyword = screen.getByText('python')
      const deleteButton = pythonKeyword.parentElement?.querySelector('button')

      await userEvent.click(deleteButton!)

      // Should show spinner while deleting
      await waitFor(() => {
        const spinner = deleteButton?.querySelector('.animate-spin')
        expect(spinner).toBeInTheDocument()
      })

      // Resolve and cleanup
      resolvePromise!()
    })
  })

  describe('Form Submission', () => {
    it('submits on Enter key press', async () => {
      const mockCreateKeyword = vi.mocked(api.createKeyword)
      mockCreateKeyword.mockResolvedValueOnce({
        id: '4',
        keyword: 'docker',
        created_at: '2024-01-16T10:00:00Z',
      })

      render(
        <KeywordManager
          keywords={[]}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      const input = screen.getByPlaceholderText('Enter a keyword...')

      await userEvent.type(input, 'docker{enter}')

      await waitFor(() => {
        expect(mockCreateKeyword).toHaveBeenCalledWith('docker')
      })
    })

    it('does not submit empty form on Enter', async () => {
      const mockCreateKeyword = vi.mocked(api.createKeyword)

      render(
        <KeywordManager
          keywords={[]}
          onKeywordChange={mockOnKeywordChange}
          loading={false}
        />
      )

      const input = screen.getByPlaceholderText('Enter a keyword...')

      fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' })

      expect(mockCreateKeyword).not.toHaveBeenCalled()
    })
  })
})

